"""Opcode handler registry and dispatch mechanism.

Complete implementation covering all 24 segments from opcodes.toml
(TIME MACHINE V4.2 — GTRON 2-Rack System).

Opcodes are registered in UPPERCASE. Both serial and HTTP entry points
normalize to uppercase before dispatch, so case is irrelevant for callers.

Handler return types:
  - (str, DeviceState)        — single response
  - (list[str], DeviceState)  — multiple responses sent back-to-back
  - ("", DeviceState)         — fire-and-forget, no serial response

Parameter opcodes:
  Some opcodes expect a second 5-byte frame on serial containing a
  parameter value (step count, RPM, delay, etc.).  These are listed in
  ``PARAM_OPCODES``.  The serial run-loop reads the extra frame and
  calls ``dispatch_with_param(opcode, state, param_str)`` instead of
  ``dispatch(opcode, state)``.
"""
import logging
import time
from typing import Callable, Dict, List, Tuple, Optional, Union, Any
from firmware_emulator.src.device_state import (
    DeviceState, GuidePosition, RunState,
)

# Handler return: response can be str or list[str] for multi-response opcodes
HandlerResponse = Union[str, List[str]]
HandlerFunc = Callable[[DeviceState], Tuple[HandlerResponse, DeviceState]]
# Param handler: receives state + parameter string from the second serial frame
ParamHandlerFunc = Callable[[DeviceState, str], Tuple[HandlerResponse, DeviceState]]

# Opcodes that expect a second 5-byte parameter frame on serial.
# main.py checks this set to decide whether to read an extra frame.
PARAM_OPCODES = frozenset({
    "TPGDI", "BMGDI",                         # Guide motor step count
    "TPRSP", "BMRSP",                         # Reeler RPM
    "RMSMF",                                   # Reeler multiplication factor
    "TPINA", "BMINA",                         # Encoder initial angle
    "TPRTH", "BMRTH",                         # Encoder teeth count
    "SKTRG",                                   # Skip trigger count
    "SPM01", "SPM02",                         # SPM delay (microseconds)
    "LONDT", "CONDT", "COFDT", "LOFDT",      # Timing configs (commented in FW)
    "TLOND", "TCOND", "TCOFD", "TLOFD",      # Timing configs (commented in FW)
})


class OpcodeHandler:
    """
    Registry and dispatcher for opcode handlers.

    Each opcode maps to a handler function with signature:
        handler(state: DeviceState) -> (response, new_state)

    Parameter opcodes (listed in PARAM_OPCODES) additionally have a
    *param handler* with signature:
        handler(state: DeviceState, param: str) -> (response, new_state)

    response is either:
      - a single string (possibly empty for fire-and-forget commands)
      - a list of strings for opcodes that send multiple frames (e.g. sag sensors)

    Handlers are stateless — they receive immutable state and return new state.
    """

    def __init__(
        self,
        logger: logging.Logger,
        delays: Optional[Dict[str, float]] = None,
    ):
        """
        Initialize OpcodeHandler.

        Args:
            logger: logging.Logger instance
            delays: Optional dict mapping opcode -> delay in seconds
                    before the response is sent.  Example:
                        {"TPGOP": 0.5, "TPGCL": 0.5}
                    Pass None or {} for instant responses.
        """
        self.logger = logger
        self.handlers: Dict[str, HandlerFunc] = {}
        self.param_handlers: Dict[str, ParamHandlerFunc] = {}
        self.delays: Dict[str, float] = delays or {}

        # Register all handlers
        self._register_builtin_handlers()

    # ── Public API ────────────────────────────────────────────────────────

    def register(self, opcode: str, handler: HandlerFunc) -> None:
        """Register a handler for an opcode (stored uppercase)."""
        key = opcode.upper()
        self.handlers[key] = handler
        self.logger.debug(f"Handler registered: {key}")

    def get_handler(self, opcode: str) -> HandlerFunc:
        """Retrieve handler; raises KeyError if not found."""
        key = opcode.upper()
        if key not in self.handlers:
            raise KeyError(f"No handler registered for opcode: {key}")
        return self.handlers[key]

    def dispatch(
        self, opcode: str, state: DeviceState,
    ) -> Tuple[HandlerResponse, DeviceState]:
        """
        Dispatch opcode to appropriate handler.

        If no handler is registered, returns "FLS" (incorrect opcode).
        """
        key = opcode.upper()
        if key not in self.handlers:
            self.logger.warning(f"Unknown opcode: {key} -> FLS")
            return "FLS", state
        handler = self.handlers[key]
        response, new_state = handler(state)
        return response, new_state

    def get_delay(self, opcode: str) -> float:
        """Return configured delay (seconds) for an opcode, or 0."""
        return self.delays.get(opcode.upper(), 0.0)

    def list_handlers(self) -> list:
        """List all registered opcode strings (sorted)."""
        return sorted(self.handlers.keys())

    def register_param(self, opcode: str, handler: ParamHandlerFunc) -> None:
        """Register a *parameter* handler for an opcode.

        A param handler has the signature:
            handler(state, param_str) -> (response, new_state)

        The base (no-param) handler is still registered via ``register()``
        so that dispatch() works for HTTP/test calls that don't supply a
        parameter.  ``dispatch_with_param()`` prefers the param handler
        when available.
        """
        key = opcode.upper()
        self.param_handlers[key] = handler
        self.logger.debug(f"Param handler registered: {key}")

    def is_param_opcode(self, opcode: str) -> bool:
        """Return True if the opcode expects a second 5-byte parameter frame."""
        return opcode.upper() in PARAM_OPCODES

    def dispatch_with_param(
        self, opcode: str, state: DeviceState, param: str,
    ) -> Tuple[HandlerResponse, DeviceState]:
        """Dispatch a parameter opcode with its parameter value.

        Falls back to the regular handler if no param handler is registered.
        """
        key = opcode.upper()
        if key in self.param_handlers:
            response, new_state = self.param_handlers[key](state, param)
            return response, new_state
        # Fallback: ignore param, dispatch normally
        return self.dispatch(key, state)

    # ── Built-in handler registration ─────────────────────────────────────

    def _register_builtin_handlers(self) -> None:
        """Register handlers for all firmware opcodes from opcodes.toml."""

        # Helper shorthand
        reg = self.register
        reg_param = self.register_param

        # ==================================================================
        # SEGMENT 1: COMMUNICATION / SYSTEM
        # ==================================================================

        def handle_query(state: DeviceState) -> Tuple[str, DeviceState]:
            """QUERY: Ping — respond YES."""
            return "YES", state
        reg("QUERY", handle_query)

        def handle_tsenb(state: DeviceState) -> Tuple[str, DeviceState]:
            """TSENB: Enable timestamp output during inspection."""
            ns = state.copy()
            ns.cameras.timestamp_enabled = True
            return "", ns
        reg("TSENB", handle_tsenb)

        # MIRSP is a response opcode but may arrive from MI; set insync flag
        def handle_mirsp(state: DeviceState) -> Tuple[str, DeviceState]:
            """MIRSP: Machine Interface response — set insync=true."""
            ns = state.copy()
            ns.insync = True
            return "", ns
        reg("MIRSP", handle_mirsp)

        # ==================================================================
        # SEGMENT 2: EMERGENCY STOP / MACHINE POWER
        # ==================================================================

        def handle_emstp_check(state: DeviceState) -> Tuple[str, DeviceState]:
            """EMSTP: Check e-stop / machine power status."""
            if state.estop_pressed:
                return "MP0", state   # Machine power OFF (e-stop pressed)
            else:
                return "MP1", state   # Machine power ON
        reg("EMSTP", handle_emstp_check)

        # ==================================================================
        # SEGMENT 3: PUSH BUTTON ATTACH / DETACH
        # ==================================================================

        def handle_atrun(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.button_flags.run = True; return "", ns
        reg("ATRUN", handle_atrun)

        def handle_dtrun(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.button_flags.run = False; return "", ns
        reg("DTRUN", handle_dtrun)

        def handle_atpau(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.button_flags.pause = True; return "", ns
        reg("ATPAU", handle_atpau)

        def handle_dtpau(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.button_flags.pause = False; return "", ns
        reg("DTPAU", handle_dtpau)

        def handle_atstp(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.button_flags.stop = True; return "", ns
        reg("ATSTP", handle_atstp)

        def handle_dtstp(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.button_flags.stop = False; return "", ns
        reg("DTSTP", handle_dtstp)

        def handle_atbof(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.button_flags.buzzeroff = True; return "", ns
        reg("ATBOF", handle_atbof)

        def handle_dtbof(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.button_flags.buzzeroff = False; return "", ns
        reg("DTBOF", handle_dtbof)

        def handle_atdrl(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.button_flags.doorlock = True; return "", ns
        reg("ATDRL", handle_atdrl)

        def handle_dtdrl(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.button_flags.doorlock = False; return "", ns
        reg("DTDRL", handle_dtdrl)

        # ==================================================================
        # SEGMENT 5: PUSH BUTTON INDICATOR LAMPS
        # ==================================================================

        def handle_runon(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.button_lamps.run = True; return "", ns
        reg("RUNON", handle_runon)

        def handle_runof(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.button_lamps.run = False; return "", ns
        reg("RUNOF", handle_runof)

        def handle_pauon(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.button_lamps.pause = True; return "", ns
        reg("PAUON", handle_pauon)

        def handle_pauof(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.button_lamps.pause = False; return "", ns
        reg("PAUOF", handle_pauof)

        def handle_stpon(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.button_lamps.stop = True; return "", ns
        reg("STPON", handle_stpon)

        def handle_stpof(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.button_lamps.stop = False; return "", ns
        reg("STPOF", handle_stpof)

        def handle_bzron(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.button_lamps.buzzer = True; return "", ns
        reg("BZRON", handle_bzron)

        def handle_bzrof(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.button_lamps.buzzer = False; return "", ns
        reg("BZROF", handle_bzrof)

        # ==================================================================
        # SEGMENT 6: TOWER LAMP
        # ==================================================================

        def handle_tred1(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.lamps.red = True; return "", ns
        reg("TRED1", handle_tred1)

        def handle_tred0(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.lamps.red = False; return "", ns
        reg("TRED0", handle_tred0)

        def handle_tyel1(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.lamps.yellow = True; return "", ns
        reg("TYEL1", handle_tyel1)

        def handle_tyel0(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.lamps.yellow = False; return "", ns
        reg("TYEL0", handle_tyel0)

        def handle_tgrn1(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.lamps.green = True; return "", ns
        reg("TGRN1", handle_tgrn1)

        def handle_tgrn0(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.lamps.green = False; return "", ns
        reg("TGRN0", handle_tgrn0)

        def handle_tbzr1(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.lamps.buzzer = True; return "", ns
        reg("TBZR1", handle_tbzr1)

        def handle_tbzr0(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.lamps.buzzer = False; return "", ns
        reg("TBZR0", handle_tbzr0)

        # ==================================================================
        # SEGMENT 7: STAMPING, WINDING & SOLENOID
        # ==================================================================

        def handle_stmp1(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.stamping_relay = True; return "", ns
        reg("STMP1", handle_stmp1)

        def handle_stmp0(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.stamping_relay = False; return "", ns
        reg("STMP0", handle_stmp0)

        def handle_wind1(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.winding_relay = True; return "", ns
        reg("WIND1", handle_wind1)

        def handle_wind0(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.winding_relay = False; return "", ns
        reg("WIND0", handle_wind0)

        def handle_solon(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.solenoid_top = True; return "", ns
        reg("SOLON", handle_solon)

        def handle_solof(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.solenoid_top = False; return "", ns
        reg("SOLOF", handle_solof)

        # ==================================================================
        # SEGMENT 8: DOOR LOCK / PRESSURE SWITCH
        # ==================================================================

        def handle_doorc(s: DeviceState) -> Tuple[str, DeviceState]:
            """DOORC: Check door lock limit switches."""
            return ("DL1" if s.door_locked else "DL0"), s
        reg("DOORC", handle_doorc)

        def handle_pswen(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.pressure_switch_enabled = True; return "", ns
        reg("PSWEN", handle_pswen)

        def handle_pswdb(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.pressure_switch_enabled = False; return "", ns
        reg("PSWDB", handle_pswdb)

        def handle_pswck(s: DeviceState) -> Tuple[str, DeviceState]:
            """PSWCK: One-shot check of pressure switch state."""
            return ("PSWON" if s.pressure_switch_on else "PSWOF"), s
        reg("PSWCK", handle_pswck)

        # ==================================================================
        # SEGMENT 9: SAG SENSOR (dual response)
        # ==================================================================

        def handle_tpsag(s: DeviceState) -> Tuple[List[str], DeviceState]:
            """TPSAG: Check top rack sag sensors — two responses."""
            r1 = "TU1" if not s.sag_top_upper else "TU0"
            r2 = "TL1" if not s.sag_top_lower else "TL0"
            return [r1, r2], s
        reg("TPSAG", handle_tpsag)

        def handle_bmsag(s: DeviceState) -> Tuple[List[str], DeviceState]:
            """BMSAG: Check bottom rack sag sensors — two responses."""
            r1 = "BU1" if not s.sag_bottom_upper else "BU0"
            r2 = "BL1" if not s.sag_bottom_lower else "BL0"
            return [r1, r2], s
        reg("BMSAG", handle_bmsag)

        # ==================================================================
        # SEGMENT 10: GUIDE MOTOR
        # ==================================================================

        def handle_tpgop(s: DeviceState) -> Tuple[str, DeviceState]:
            """tpGOP: Open top guide motor."""
            ns = s.copy()
            ns.guide_top.position = GuidePosition.OPEN
            ns.guide_top.reached_limit = True  # open limit reached
            return "TPGOR", ns
        reg("TPGOP", handle_tpgop)

        def handle_tpgcl(s: DeviceState) -> Tuple[str, DeviceState]:
            """tpGCL: Close top guide motor."""
            ns = s.copy()
            ns.guide_top.position = GuidePosition.CLOSED
            ns.guide_top.reached_limit = False
            return "TPGCR", ns
        reg("TPGCL", handle_tpgcl)

        def handle_bmgop(s: DeviceState) -> Tuple[str, DeviceState]:
            """bmGOP: Open bottom guide motor."""
            ns = s.copy()
            ns.guide_bottom.position = GuidePosition.OPEN
            ns.guide_bottom.reached_limit = True
            return "BMGOR", ns
        reg("BMGOP", handle_bmgop)

        def handle_bmgcl(s: DeviceState) -> Tuple[str, DeviceState]:
            """bmGCL: Close bottom guide motor."""
            ns = s.copy()
            ns.guide_bottom.position = GuidePosition.CLOSED
            ns.guide_bottom.reached_limit = False
            return "BMGCR", ns
        reg("BMGCL", handle_bmgcl)

        def handle_tpgdi(s: DeviceState) -> Tuple[str, DeviceState]:
            """tpGDI: Move top guide to steps — close guide (no response)."""
            ns = s.copy()
            ns.guide_top.position = GuidePosition.CLOSED
            return "", ns
        reg("TPGDI", handle_tpgdi)

        def handle_tpgdi_param(s: DeviceState, param: str) -> Tuple[str, DeviceState]:
            """tpGDI with param: step count (e.g. 5000) — set guide CLOSED."""
            ns = s.copy()
            ns.guide_top.position = GuidePosition.CLOSED
            return "", ns
        reg_param("TPGDI", handle_tpgdi_param)

        def handle_bmgdi(s: DeviceState) -> Tuple[str, DeviceState]:
            """bmGDI: Move bottom guide to steps — close guide (no response)."""
            ns = s.copy()
            ns.guide_bottom.position = GuidePosition.CLOSED
            return "", ns
        reg("BMGDI", handle_bmgdi)

        def handle_bmgdi_param(s: DeviceState, param: str) -> Tuple[str, DeviceState]:
            """bmGDI with param: step count (e.g. 5000) — set guide CLOSED."""
            ns = s.copy()
            ns.guide_bottom.position = GuidePosition.CLOSED
            return "", ns
        reg_param("BMGDI", handle_bmgdi_param)

        def handle_tpgts(s: DeviceState) -> Tuple[str, DeviceState]:
            """tpGTS: Top guide test — open then close sequence."""
            ns = s.copy()
            ns.guide_top.position = GuidePosition.OPEN
            return "", ns
        reg("TPGTS", handle_tpgts)

        def handle_bmgts(s: DeviceState) -> Tuple[str, DeviceState]:
            """bmGTS: Bottom guide test — open then close sequence."""
            ns = s.copy()
            ns.guide_bottom.position = GuidePosition.OPEN
            return "", ns
        reg("BMGTS", handle_bmgts)

        # ==================================================================
        # SEGMENT 11: LIMIT SWITCH CHECK
        # ==================================================================

        def handle_tplsc(s: DeviceState) -> Tuple[str, DeviceState]:
            """tpLSC: Check top open limit switch."""
            return ("TPOL1" if s.guide_top.reached_limit else "TPOL0"), s
        reg("TPLSC", handle_tplsc)

        def handle_bmlsc(s: DeviceState) -> Tuple[str, DeviceState]:
            """bmLSC: Check bottom open limit switch."""
            return ("BMOL1" if s.guide_bottom.reached_limit else "BMOL0"), s
        reg("BMLSC", handle_bmlsc)

        # ==================================================================
        # SEGMENT 12: STEPPER / REELER MOTOR INITIALIZATION
        # ==================================================================

        def handle_smini(s: DeviceState) -> Tuple[str, DeviceState]:
            """SMINI: Initialize stepper drivers (TMC5160 SPI config)."""
            ns = s.copy()
            ns.stepper_initialized = True
            return "", ns
        reg("SMINI", handle_smini)

        def handle_rmini(s: DeviceState) -> Tuple[str, DeviceState]:
            """RMINI: Initialize reeler motors (GCONF)."""
            ns = s.copy()
            ns.reeler_initialized = True
            return "", ns
        reg("RMINI", handle_rmini)

        # ==================================================================
        # SEGMENT 13: REELER MOTOR CONTROL
        # ==================================================================

        def handle_tpstr(s: DeviceState) -> Tuple[str, DeviceState]:
            """tpSTR: Start top reeler motor."""
            ns = s.copy()
            ns.reeler_top.running = True
            return "", ns
        reg("TPSTR", handle_tpstr)

        def handle_tpstp(s: DeviceState) -> Tuple[str, DeviceState]:
            """tpSTP: Stop top reeler motor."""
            ns = s.copy()
            ns.reeler_top.running = False
            return "", ns
        reg("TPSTP", handle_tpstp)

        def handle_bmstr(s: DeviceState) -> Tuple[str, DeviceState]:
            """bmSTR: Start bottom reeler motor."""
            ns = s.copy()
            ns.reeler_bottom.running = True
            return "", ns
        reg("BMSTR", handle_bmstr)

        def handle_bmstp(s: DeviceState) -> Tuple[str, DeviceState]:
            """bmSTP: Stop bottom reeler motor."""
            ns = s.copy()
            ns.reeler_bottom.running = False
            return "", ns
        reg("BMSTP", handle_bmstp)

        def handle_tprsp(s: DeviceState) -> Tuple[str, DeviceState]:
            """tpRSP: Set top reeler speed — no response."""
            return "", s
        reg("TPRSP", handle_tprsp)

        def handle_tprsp_param(s: DeviceState, param: str) -> Tuple[str, DeviceState]:
            """tpRSP with param: RPM value (e.g. 200) — store in reeler_top.speed."""
            ns = s.copy()
            try:
                ns.reeler_top.speed = int(param.strip())
            except (ValueError, AttributeError):
                pass  # Malformed param — ignore
            return "", ns
        reg_param("TPRSP", handle_tprsp_param)

        def handle_bmrsp(s: DeviceState) -> Tuple[str, DeviceState]:
            """bmRSP: Set bottom reeler speed — no response."""
            return "", s
        reg("BMRSP", handle_bmrsp)

        def handle_bmrsp_param(s: DeviceState, param: str) -> Tuple[str, DeviceState]:
            """bmRSP with param: RPM value (e.g. 200) — store in reeler_bottom.speed."""
            ns = s.copy()
            try:
                ns.reeler_bottom.speed = int(param.strip())
            except (ValueError, AttributeError):
                pass  # Malformed param — ignore
            return "", ns
        reg_param("BMRSP", handle_bmrsp_param)

        def handle_tprtr(s: DeviceState) -> Tuple[str, DeviceState]:
            """tpRTR: Rotate top reeler (diagnostic) — responds RHD when done."""
            ns = s.copy()
            ns.reeler_top.running = True
            return "RHD", ns
        reg("TPRTR", handle_tprtr)

        def handle_bmrtr(s: DeviceState) -> Tuple[str, DeviceState]:
            """bmRTR: Rotate bottom reeler (diagnostic) — responds RHD."""
            ns = s.copy()
            ns.reeler_bottom.running = True
            return "RHD", ns
        reg("BMRTR", handle_bmrtr)

        def handle_rmsmf(s: DeviceState) -> Tuple[str, DeviceState]:
            """RMSMF: Set reeler multiplication factor — ignore, no response."""
            return "", s
        reg("RMSMF", handle_rmsmf)

        # ==================================================================
        # SEGMENT 14: ENCODER
        # ==================================================================

        def handle_tpeni(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.encoder_top.initialized = True; return "", ns
        reg("TPENI", handle_tpeni)

        def handle_bmeni(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.encoder_bottom.initialized = True; return "", ns
        reg("BMENI", handle_bmeni)

        def handle_tpina(s: DeviceState) -> Tuple[str, DeviceState]:
            """tpINA: Set top encoder initial angle — ignore, no response."""
            return "", s
        reg("TPINA", handle_tpina)

        def handle_bmina(s: DeviceState) -> Tuple[str, DeviceState]:
            """bmINA: Set bottom encoder initial angle — ignore, no response."""
            return "", s
        reg("BMINA", handle_bmina)

        def handle_tpeen(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.encoder_top.enabled = True; return "", ns
        reg("TPEEN", handle_tpeen)

        def handle_tpedb(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.encoder_top.enabled = False; return "", ns
        reg("TPEDB", handle_tpedb)

        def handle_bmeen(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.encoder_bottom.enabled = True; return "", ns
        reg("BMEEN", handle_bmeen)

        def handle_bmedb(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.encoder_bottom.enabled = False; return "", ns
        reg("BMEDB", handle_bmedb)

        def handle_tprth(s: DeviceState) -> Tuple[str, DeviceState]:
            """tpRTH: Set top reeler teeth count — ignore, no response."""
            return "", s
        reg("TPRTH", handle_tprth)

        def handle_bmrth(s: DeviceState) -> Tuple[str, DeviceState]:
            """bmRTH: Set bottom reeler teeth count — ignore, no response."""
            return "", s
        reg("BMRTH", handle_bmrth)

        def handle_sktrg(s: DeviceState) -> Tuple[str, DeviceState]:
            """SKTRG: Set skip trigger count — ignore, no response."""
            return "", s
        reg("SKTRG", handle_sktrg)

        # ==================================================================
        # SEGMENT 15: TRIGGER SENSOR POWER (POS01-08 / PFS01-08)
        # ==================================================================

        for n in range(1, 9):
            padded = f"{n:02d}"

            def _make_pon(sensor_num: int):
                def handler(s: DeviceState) -> Tuple[str, DeviceState]:
                    ns = s.copy()
                    ns.sensor_power[sensor_num] = True
                    return "", ns
                return handler

            def _make_poff(sensor_num: int):
                def handler(s: DeviceState) -> Tuple[str, DeviceState]:
                    ns = s.copy()
                    ns.sensor_power[sensor_num] = False
                    return "", ns
                return handler

            reg(f"POS{padded}", _make_pon(n))
            reg(f"PFS{padded}", _make_poff(n))

        # ==================================================================
        # SEGMENT 16: TRIGGER SENSOR ATTACH / DETACH & CHECK
        # ==================================================================

        def handle_tpats(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy()
            ns.sensor_top.attached = True
            ns.sensor_top.powered = True
            return "", ns
        reg("TPATS", handle_tpats)

        def handle_tpdts(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy()
            ns.sensor_top.attached = False
            ns.sensor_top.powered = False
            return "", ns
        reg("TPDTS", handle_tpdts)

        def handle_bmats(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy()
            ns.sensor_bottom.attached = True
            ns.sensor_bottom.powered = True
            return "", ns
        reg("BMATS", handle_bmats)

        def handle_bmdts(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy()
            ns.sensor_bottom.attached = False
            ns.sensor_bottom.powered = False
            return "", ns
        reg("BMDTS", handle_bmdts)

        def handle_tpsck(s: DeviceState) -> Tuple[str, DeviceState]:
            """TPSCK: Check top trigger sensor state."""
            return ("TS1" if s.sensor_top.triggered else "TS0"), s
        reg("TPSCK", handle_tpsck)

        def handle_bpsck(s: DeviceState) -> Tuple[str, DeviceState]:
            """BPSCK: Check bottom trigger sensor state."""
            return ("BS1" if s.sensor_bottom.triggered else "BS0"), s
        reg("BPSCK", handle_bpsck)

        # ==================================================================
        # SEGMENT 17: LIGHT / CAMERA SEQUENCES
        # ==================================================================

        def handle_lcs01(s: DeviceState) -> Tuple[str, DeviceState]:
            """LCS01: Rack 1 Top Cam."""
            ns = s.copy(); ns.cameras.flags[0] = True; ns.cameras.active_sequence = 1; return "", ns
        reg("LCS01", handle_lcs01)

        def handle_lcs02(s: DeviceState) -> Tuple[str, DeviceState]:
            """LCS02: Rack 1 Side Cam."""
            ns = s.copy(); ns.cameras.flags[1] = True; ns.cameras.active_sequence = 2; return "", ns
        reg("LCS02", handle_lcs02)

        def handle_lcs03(s: DeviceState) -> Tuple[str, DeviceState]:
            """LCS03: Rack 1 Front Cam."""
            ns = s.copy(); ns.cameras.flags[2] = True; ns.cameras.active_sequence = 3; return "", ns
        reg("LCS03", handle_lcs03)

        def handle_lcs04(s: DeviceState) -> Tuple[str, DeviceState]:
            """LCS04: Rack 1 Top Light Cam (solenoid)."""
            ns = s.copy(); ns.cameras.flags[3] = True; ns.cameras.active_sequence = 4; return "", ns
        reg("LCS04", handle_lcs04)

        def handle_lcs05(s: DeviceState) -> Tuple[str, DeviceState]:
            """LCS05: Rack 2 Top Cam."""
            ns = s.copy(); ns.cameras.flags[4] = True; ns.cameras.active_sequence = 5; return "", ns
        reg("LCS05", handle_lcs05)

        def handle_lcs06(s: DeviceState) -> Tuple[str, DeviceState]:
            """LCS06: Rack 2 Side Cam."""
            ns = s.copy(); ns.cameras.flags[5] = True; ns.cameras.active_sequence = 6; return "", ns
        reg("LCS06", handle_lcs06)

        def handle_lcs07(s: DeviceState) -> Tuple[str, DeviceState]:
            """LCS07: Rack 2 Front Cam."""
            ns = s.copy(); ns.cameras.flags[6] = True; ns.cameras.active_sequence = 7; return "", ns
        reg("LCS07", handle_lcs07)

        def handle_lcstp(s: DeviceState) -> Tuple[str, DeviceState]:
            """LCStp: Full top rack sequence (cameras 0-2 + 3 backlight)."""
            ns = s.copy()
            for i in range(4):
                ns.cameras.flags[i] = True
            ns.cameras.active_sequence = -1
            return "", ns
        reg("LCSTP", handle_lcstp)

        def handle_lcsbm(s: DeviceState) -> Tuple[str, DeviceState]:
            """LCSbm: Full bottom rack sequence (cameras 4-6)."""
            ns = s.copy()
            for i in range(4, 7):
                ns.cameras.flags[i] = True
            ns.cameras.active_sequence = -2
            return "", ns
        reg("LCSBM", handle_lcsbm)

        # ==================================================================
        # SEGMENT 18: LIGHT / CAMERA SEQUENCE FLAGS (Inspection Enable)
        # ==================================================================

        for cam_idx in range(7):
            def _make_lcsi(idx: int):
                def handler(s: DeviceState) -> Tuple[str, DeviceState]:
                    ns = s.copy()
                    ns.cameras.inspection_flags[idx] = True
                    return "", ns
                return handler
            reg(f"LCSI{cam_idx}", _make_lcsi(cam_idx))

        # ==================================================================
        # SEGMENT 19: LIGHT / CAMERA TIMING CONFIG
        # (Commented out in firmware — accept param silently, no-op)
        # ==================================================================

        for _timing_op in ("LONDT", "CONDT", "COFDT", "LOFDT",
                           "TLOND", "TCOND", "TCOFD", "TLOFD"):
            def _make_timing_noop(op=_timing_op):
                def handler(s: DeviceState) -> Tuple[str, DeviceState]:
                    return "", s
                handler.__doc__ = f"{op}: Timing config — commented out in firmware, no-op."
                return handler
            reg(_timing_op, _make_timing_noop())

        # ==================================================================
        # SEGMENT 20: IET (INSPECTION EVENT TRANSITIONS)
        # ==================================================================

        def handle_iesel(s: DeviceState) -> Tuple[str, DeviceState]:
            """IESEL: Select state — enable RUN, disable others, RUN lamp ON."""
            ns = s.copy()
            ns.button_flags.run = True
            ns.button_flags.pause = False
            ns.button_flags.stop = False
            ns.button_flags.buzzeroff = False
            ns.button_lamps.run = True
            ns.button_lamps.pause = False
            ns.button_lamps.stop = False
            ns.button_lamps.buzzer = False
            # Reset tower lamps
            ns.lamps.red = False
            ns.lamps.yellow = False
            ns.lamps.green = False
            ns.lamps.buzzer = False
            return "", ns
        reg("IESEL", handle_iesel)

        def handle_ierun(s: DeviceState) -> Tuple[str, DeviceState]:
            """IERUN: Run state — enable PAUSE+STOP, green lamp ON, solenoid ON."""
            ns = s.copy()
            ns.button_flags.run = False
            ns.button_flags.pause = True
            ns.button_flags.stop = True
            ns.button_flags.buzzeroff = False
            ns.lamps.green = True
            ns.lamps.yellow = False
            ns.lamps.red = False
            ns.lamps.buzzer = False
            ns.solenoid_top = True
            return "", ns
        reg("IERUN", handle_ierun)

        def handle_iepas(s: DeviceState) -> Tuple[str, DeviceState]:
            """IEPAS: Pass state — same as Run."""
            ns = s.copy()
            ns.button_flags.run = False
            ns.button_flags.pause = True
            ns.button_flags.stop = True
            ns.lamps.green = True
            ns.lamps.yellow = False
            ns.lamps.red = False
            ns.lamps.buzzer = False
            return "", ns
        reg("IEPAS", handle_iepas)

        def handle_iepau(s: DeviceState) -> Tuple[str, DeviceState]:
            """IEPAU: Pause state — enable RUN+STOP, yellow lamp, close stamping+solenoid."""
            ns = s.copy()
            ns.button_flags.run = True
            ns.button_flags.pause = False
            ns.button_flags.stop = True
            ns.button_flags.buzzeroff = False
            ns.lamps.green = False
            ns.lamps.yellow = True
            ns.lamps.red = False
            ns.lamps.buzzer = False
            ns.stamping_relay = False
            ns.solenoid_top = False
            return "", ns
        reg("IEPAU", handle_iepau)

        def handle_iefai(s: DeviceState) -> Tuple[str, DeviceState]:
            """IEFAI: Fail state — enable BUZZEROFF only, red lamp + buzzer ON."""
            ns = s.copy()
            ns.button_flags.run = False
            ns.button_flags.pause = False
            ns.button_flags.stop = False
            ns.button_flags.buzzeroff = True
            ns.lamps.green = False
            ns.lamps.yellow = False
            ns.lamps.red = True
            ns.lamps.buzzer = True
            ns.stamping_relay = False
            ns.solenoid_top = False
            return "", ns
        reg("IEFAI", handle_iefai)

        def handle_bofdr(s: DeviceState) -> Tuple[str, DeviceState]:
            """BOFDR: Buzzer off during run — disable RUN, enable STOP, buzzer OFF."""
            ns = s.copy()
            ns.button_flags.run = False
            ns.button_flags.stop = True
            ns.button_flags.buzzeroff = False
            ns.lamps.buzzer = False
            return "", ns
        reg("BOFDR", handle_bofdr)

        def handle_bofer(s: DeviceState) -> Tuple[str, DeviceState]:
            """BOFER: Buzzer off error recovery — enable RUN+STOP, buzzer OFF."""
            ns = s.copy()
            ns.button_flags.run = True
            ns.button_flags.stop = True
            ns.button_flags.buzzeroff = False
            ns.lamps.buzzer = False
            return "", ns
        reg("BOFER", handle_bofer)

        def handle_iedrl(s: DeviceState) -> Tuple[str, DeviceState]:
            """IEDRL: Door lock poka-yoke — accept silently."""
            return "", s
        reg("IEDRL", handle_iedrl)

        def handle_dhbls(s: DeviceState) -> Tuple[str, DeviceState]:
            """DHBLS: Full reset — disable all buttons/motors/interrupts/sensors."""
            ns = s.copy()
            # Disable all button flags
            ns.button_flags.run = False
            ns.button_flags.pause = False
            ns.button_flags.stop = False
            ns.button_flags.buzzeroff = False
            ns.button_flags.doorlock = False
            # Turn off all button lamps
            ns.button_lamps.run = False
            ns.button_lamps.pause = False
            ns.button_lamps.stop = False
            ns.button_lamps.buzzer = False
            # Turn off all tower lamps
            ns.lamps.red = False
            ns.lamps.yellow = False
            ns.lamps.green = False
            ns.lamps.buzzer = False
            # Stop motors
            ns.reeler_top.running = False
            ns.reeler_bottom.running = False
            # Disable sensors
            ns.sensor_top.attached = False
            ns.sensor_top.powered = False
            ns.sensor_bottom.attached = False
            ns.sensor_bottom.powered = False
            # Disable encoders
            ns.encoder_top.enabled = False
            ns.encoder_bottom.enabled = False
            # Close solenoid/stamping
            ns.solenoid_top = False
            ns.solenoid_bottom = False
            ns.stamping_relay = False
            ns.winding_relay = False
            # Reset camera flags
            for i in range(7):
                ns.cameras.flags[i] = False
                ns.cameras.inspection_flags[i] = False
            ns.cameras.active_sequence = -1
            # Power off all sensors
            for i in range(1, 9):
                ns.sensor_power[i] = False
            # Disable rejection & pressure switch
            ns.rejection_enabled = False
            ns.pressure_switch_enabled = False
            return "", ns
        reg("DHBLS", handle_dhbls)

        def handle_hwbdb(s: DeviceState) -> Tuple[str, DeviceState]:
            """HWBDB: Disable all hardware buttons, turn off all indicator lamps."""
            ns = s.copy()
            ns.button_flags.run = False
            ns.button_flags.pause = False
            ns.button_flags.stop = False
            ns.button_flags.buzzeroff = False
            ns.button_flags.doorlock = False
            ns.button_lamps.run = False
            ns.button_lamps.pause = False
            ns.button_lamps.stop = False
            ns.button_lamps.buzzer = False
            return "", ns
        reg("HWBDB", handle_hwbdb)

        # ==================================================================
        # SEGMENT 21: REFERENCE SEARCH
        # ==================================================================

        def handle_rfs01(s: DeviceState) -> Tuple[str, DeviceState]:
            """RFS01: Top camera reference search — responds TRD01."""
            return "TRD01", s
        reg("RFS01", handle_rfs01)

        def handle_rfs02(s: DeviceState) -> Tuple[str, DeviceState]:
            """RFS02: Bottom camera reference search — responds TRD02."""
            return "TRD02", s
        reg("RFS02", handle_rfs02)

        def handle_spm01(s: DeviceState) -> Tuple[str, DeviceState]:
            """SPM01: Set top SPM delay — no response."""
            return "", s
        reg("SPM01", handle_spm01)

        def handle_spm01_param(s: DeviceState, param: str) -> Tuple[str, DeviceState]:
            """SPM01 with param: delay in microseconds (e.g. 3000)."""
            ns = s.copy()
            try:
                ns.spm_delay_top = int(param.strip())
            except (ValueError, AttributeError):
                pass
            return "", ns
        reg_param("SPM01", handle_spm01_param)

        def handle_spm02(s: DeviceState) -> Tuple[str, DeviceState]:
            """SPM02: Set bottom SPM delay — no response."""
            return "", s
        reg("SPM02", handle_spm02)

        def handle_spm02_param(s: DeviceState, param: str) -> Tuple[str, DeviceState]:
            """SPM02 with param: delay in microseconds (e.g. 3000)."""
            ns = s.copy()
            try:
                ns.spm_delay_bottom = int(param.strip())
            except (ValueError, AttributeError):
                pass
            return "", ns
        reg_param("SPM02", handle_spm02_param)

        # ==================================================================
        # SEGMENT 22: REJECTION LOGIC
        # ==================================================================

        def handle_rjenb(s: DeviceState) -> Tuple[str, DeviceState]:
            """RJENB: Enable rejection logic."""
            ns = s.copy()
            ns.rejection_enabled = True
            return "", ns
        reg("RJENB", handle_rjenb)

        # ==================================================================
        # SEGMENT 23: I2C EXPANDER INITIALIZATION
        # ==================================================================

        def handle_i2c1(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.i2c_initialized[1] = True; return "", ns
        reg("I2C1", handle_i2c1)

        def handle_i2c2(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.i2c_initialized[2] = True; return "", ns
        reg("I2C2", handle_i2c2)

        def handle_i2c3(s: DeviceState) -> Tuple[str, DeviceState]:
            ns = s.copy(); ns.i2c_initialized[3] = True; return "", ns
        reg("I2C3", handle_i2c3)

        # ==================================================================
        # EMULATOR-ONLY OPCODES (UI Control Buttons)
        # ==================================================================
        # These are NOT part of the real hardware protocol.
        # They exist for the dashboard UI to control emulator run state.

        def handle_emrun(s: DeviceState) -> Tuple[str, DeviceState]:
            """EMRUN: Set emulator to RUNNING."""
            ns = s.copy()
            ns.run_state = RunState.RUNNING
            return "EMROK", ns
        reg("EMRUN", handle_emrun)

        def handle_empau(s: DeviceState) -> Tuple[str, DeviceState]:
            """EMPAU: Set emulator to PAUSED."""
            ns = s.copy()
            ns.run_state = RunState.PAUSED
            return "EMPOK", ns
        reg("EMPAU", handle_empau)

        def handle_emest(s: DeviceState) -> Tuple[str, DeviceState]:
            """EMEST: Set emulator to STOPPED (renamed from EMSTP to avoid collision)."""
            ns = s.copy()
            ns.run_state = RunState.STOPPED
            return "EMSOK", ns
        reg("EMEST", handle_emest)

        def handle_bzzof(s: DeviceState) -> Tuple[str, DeviceState]:
            """BZZOF: Buzzer override (silence buzzer)."""
            ns = s.copy()
            ns.buzzer_override = True
            return "BZZOK", ns
        reg("BZZOF", handle_bzzof)
