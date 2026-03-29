"""Opcode handler registry and dispatch mechanism."""
import logging
from typing import Callable, Dict, Tuple, Optional, Any
from firmware_emulator.src.device_state import DeviceState, GuidePosition


# Handler function signature: (state) -> (response, new_state)
HandlerFunc = Callable[[DeviceState], Tuple[str, DeviceState]]


class OpcodeHandler:
    """
    Registry and dispatcher for opcode handlers.
    
    Each opcode maps to a handler function with signature:
        handler(state: DeviceState) -> (response: str, new_state: DeviceState)
    
    Handlers are stateless - they receive immutable state and return new state.
    """
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize OpcodeHandler with logger.
        
        Args:
            logger: logging.Logger instance
        """
        self.logger = logger
        self.handlers: Dict[str, HandlerFunc] = {}
        
        # Register built-in handlers
        self._register_builtin_handlers()
    
    def register(self, opcode: str, handler: HandlerFunc) -> None:
        """
        Register a handler for an opcode.
        
        Args:
            opcode: Opcode string (e.g., 'QUERY', 'tpGOP')
            handler: Handler function with signature (state) -> (response, new_state)
        """
        self.handlers[opcode] = handler
        self.logger.info(f"Handler registered for opcode: {opcode}")
    
    def get_handler(self, opcode: str) -> HandlerFunc:
        """
        Retrieve a handler for an opcode.
        
        Args:
            opcode: Opcode string
        
        Returns:
            Handler function
        
        Raises:
            KeyError: If opcode has no registered handler
        """
        if opcode not in self.handlers:
            raise KeyError(f"No handler registered for opcode: {opcode}")
        return self.handlers[opcode]
    
    def dispatch(self, opcode: str, state: DeviceState) -> Tuple[str, DeviceState]:
        """
        Dispatch opcode to appropriate handler.
        
        Args:
            opcode: Opcode string
            state: Current DeviceState
        
        Returns:
            Tuple (response, new_state)
        
        Raises:
            KeyError: If opcode has no registered handler
        """
        handler = self.get_handler(opcode)
        response, new_state = handler(state)
        return response, new_state
    
    def list_handlers(self) -> list:
        """
        List all registered opcode handlers.
        
        Returns:
            List of registered opcode strings
        """
        return sorted(self.handlers.keys())
    
    def _register_builtin_handlers(self) -> None:
        """Register built-in handlers for all firmware opcodes."""
        # ===== COMMUNICATION & HANDSHAKE =====
        def handle_query(state: DeviceState) -> Tuple[str, DeviceState]:
            """QUERY: Ping command - device is alive."""
            return "YES", state
        
        self.register("QUERY", handle_query)
        
        # ===== INITIALIZATION =====
        def handle_smini(state: DeviceState) -> Tuple[str, DeviceState]:
            """SMINI: Initialize communication board."""
            # No response expected for SMINI
            return "", state
        
        self.register("SMINI", handle_smini)
        
        # ===== DOOR LOCK =====
        def handle_doorc(state: DeviceState) -> Tuple[str, DeviceState]:
            """DOORC: Check door lock status."""
            response = "DL1" if state.door_locked else "DL0"
            return response, state
        
        self.register("DOORC", handle_doorc)
        
        def handle_atdrl(state: DeviceState) -> Tuple[str, DeviceState]:
            """ATDRL: Enable/Attach door lock."""
            new_state = state.copy()
            new_state.door_locked = True
            return "", new_state
        
        self.register("ATDRL", handle_atdrl)
        
        def handle_dtdrl(state: DeviceState) -> Tuple[str, DeviceState]:
            """DTDRL: Disable/Detach door lock."""
            new_state = state.copy()
            new_state.door_locked = False
            return "", new_state
        
        self.register("DTDRL", handle_dtdrl)
        
        # ===== GUIDE MOTOR CONTROL (TOP) =====
        def handle_tpgop(state: DeviceState) -> Tuple[str, DeviceState]:
            """tpGOP: Open top guide motor."""
            new_state = state.copy()
            new_state.guide_top.position = GuidePosition.OPEN
            return "TPGOR", new_state  # TPGOR = Guide Open Response
        
        self.register("TPGOP", handle_tpgop)
        
        def handle_tpgcl(state: DeviceState) -> Tuple[str, DeviceState]:
            """tpGCL: Close top guide motor."""
            new_state = state.copy()
            new_state.guide_top.position = GuidePosition.CLOSED
            return "TPGCR", new_state  # TPGCR = Guide Close Response
        
        self.register("TPGCL", handle_tpgcl)
        
        def handle_tprtr(state: DeviceState) -> Tuple[str, DeviceState]:
            """tpRTR: Rotate top reeler motor."""
            new_state = state.copy()
            new_state.reeler_top.running = True
            return "", new_state
        
        self.register("TPRTR", handle_tprtr)
        
        def handle_tpgdi(state: DeviceState) -> Tuple[str, DeviceState]:
            """tpGDI: Set guide distance index (motor steps for ready positions)."""
            # Phase 1: Accept command without parameters
            return "", state
        
        self.register("TPGDI", handle_tpgdi)
        
        # ===== LIMIT SWITCH STATUS (TOP) =====
        def handle_tplsc(state: DeviceState) -> Tuple[str, DeviceState]:
            """tpLSC: Check top limit switch status."""
            # Check if at limit position
            if state.guide_top.reached_limit:
                return "TPOL1", state  # Limit pressed
            else:
                return "TPOL0", state  # Limit not pressed
        
        self.register("TPLSC", handle_tplsc)
        
        # ===== SENSOR CONTROL (TOP) =====
        def handle_tpats(state: DeviceState) -> Tuple[str, DeviceState]:
            """tpATS: Attach/Enable top sensor."""
            new_state = state.copy()
            new_state.sensor_top.attached = True
            new_state.sensor_top.powered = True
            return "", new_state
        
        self.register("TPATS", handle_tpats)
        
        def handle_tpdts(state: DeviceState) -> Tuple[str, DeviceState]:
            """tpDTS: Detach/Disable top sensor."""
            new_state = state.copy()
            new_state.sensor_top.attached = False
            new_state.sensor_top.powered = False
            return "", new_state
        
        self.register("TPDTS", handle_tpdts)
        
        # ===== ENCODER CONTROL (TOP) =====
        def handle_tpeni(state: DeviceState) -> Tuple[str, DeviceState]:
            """tpENI: Initialize top encoder."""
            new_state = state.copy()
            new_state.encoder_top.initialized = True
            return "", new_state
        
        self.register("TPENI", handle_tpeni)
        
        def handle_tpeen(state: DeviceState) -> Tuple[str, DeviceState]:
            """tpEEN: Enable top encoder."""
            new_state = state.copy()
            new_state.encoder_top.enabled = True
            return "", new_state
        
        self.register("TPEEN", handle_tpeen)
        
        def handle_tpedb(state: DeviceState) -> Tuple[str, DeviceState]:
            """tpEDB: Disable top encoder."""
            new_state = state.copy()
            new_state.encoder_top.enabled = False
            return "", new_state
        
        self.register("TPEDB", handle_tpedb)
        
        def handle_tprsp(state: DeviceState) -> Tuple[str, DeviceState]:
            """tpRSP: Set encoder starting position."""
            new_state = state.copy()
            new_state.encoder_top.position = 0
            return "", new_state
        
        self.register("TPRSP", handle_tprsp)
        
        def handle_tprth(state: DeviceState) -> Tuple[str, DeviceState]:
            """tpRTH: Set encoder teeth/resolution."""
            new_state = state.copy()
            # Parse teeth count if provided (Phase 2)
            return "", new_state
        
        self.register("TPRTH", handle_tprth)
        
        def handle_tpina(state: DeviceState) -> Tuple[str, DeviceState]:
            """tpINA: Set encoder index."""
            new_state = state.copy()
            new_state.encoder_top.initial_angle = 0
            return "", new_state
        
        self.register("TPINA", handle_tpina)
        
        # ===== GUIDE MOTOR CONTROL (BOTTOM) =====
        def handle_bmgop(state: DeviceState) -> Tuple[str, DeviceState]:
            """bmGOP: Open bottom guide motor."""
            new_state = state.copy()
            new_state.guide_bottom.position = GuidePosition.OPEN
            return "BMGOR", new_state
        
        self.register("BMGOP", handle_bmgop)
        
        def handle_bmgcl(state: DeviceState) -> Tuple[str, DeviceState]:
            """bmGCL: Close bottom guide motor."""
            new_state = state.copy()
            new_state.guide_bottom.position = GuidePosition.CLOSED
            return "BMGCR", new_state
        
        self.register("BMGCL", handle_bmgcl)
        
        def handle_bmrtr(state: DeviceState) -> Tuple[str, DeviceState]:
            """bmRTR: Rotate bottom reeler motor."""
            new_state = state.copy()
            new_state.reeler_bottom.running = True
            return "", new_state
        
        self.register("BMRTR", handle_bmrtr)
        
        def handle_bmgdi(state: DeviceState) -> Tuple[str, DeviceState]:
            """bmGDI: Set bottom guide distance index."""
            return "", state
        
        self.register("BMGDI", handle_bmgdi)
        
        # ===== LIMIT SWITCH STATUS (BOTTOM) =====
        def handle_bmlsc(state: DeviceState) -> Tuple[str, DeviceState]:
            """bmLSC: Check bottom limit switch status."""
            if state.guide_bottom.reached_limit:
                return "BMOL1", state
            else:
                return "BMOL0", state
        
        self.register("BMLSC", handle_bmlsc)
        
        # ===== SENSOR CONTROL (BOTTOM) =====
        def handle_bmats(state: DeviceState) -> Tuple[str, DeviceState]:
            """bmATS: Attach/Enable bottom sensor."""
            new_state = state.copy()
            new_state.sensor_bottom.attached = True
            new_state.sensor_bottom.powered = True
            return "", new_state
        
        self.register("BMATS", handle_bmats)
        
        def handle_bmdts(state: DeviceState) -> Tuple[str, DeviceState]:
            """bmDTS: Detach/Disable bottom sensor."""
            new_state = state.copy()
            new_state.sensor_bottom.attached = False
            new_state.sensor_bottom.powered = False
            return "", new_state
        
        self.register("BMDTS", handle_bmdts)
        
        # ===== ENCODER CONTROL (BOTTOM) =====
        def handle_bmeni(state: DeviceState) -> Tuple[str, DeviceState]:
            """bmENI: Initialize bottom encoder."""
            new_state = state.copy()
            new_state.encoder_bottom.initialized = True
            return "", new_state
        
        self.register("BMENI", handle_bmeni)
        
        def handle_bmeen(state: DeviceState) -> Tuple[str, DeviceState]:
            """bmEEN: Enable bottom encoder."""
            new_state = state.copy()
            new_state.encoder_bottom.enabled = True
            return "", new_state
        
        self.register("BMEEN", handle_bmeen)
        
        def handle_bmedb(state: DeviceState) -> Tuple[str, DeviceState]:
            """bmEDB: Disable bottom encoder."""
            new_state = state.copy()
            new_state.encoder_bottom.enabled = False
            return "", new_state
        
        self.register("BMEDB", handle_bmedb)
        
        def handle_bmrsp(state: DeviceState) -> Tuple[str, DeviceState]:
            """bmRSP: Set bottom encoder starting position."""
            new_state = state.copy()
            new_state.encoder_bottom.position = 0
            return "", new_state
        
        self.register("BMRSP", handle_bmrsp)
        
        def handle_bmrth(state: DeviceState) -> Tuple[str, DeviceState]:
            """bmRTH: Set bottom encoder teeth/resolution."""
            return "", state
        
        self.register("BMRTH", handle_bmrth)
        
        def handle_bmina(state: DeviceState) -> Tuple[str, DeviceState]:
            """bmINA: Set bottom encoder index."""
            new_state = state.copy()
            new_state.encoder_bottom.initial_angle = 0
            return "", new_state
        
        self.register("BMINA", handle_bmina)
        
        # ===== LIGHT & CAMERA SEQUENCES =====
        def handle_lcs01(state: DeviceState) -> Tuple[str, DeviceState]:
            """LCS01: Trigger light-camera sequence 1."""
            new_state = state.copy()
            new_state.cameras.flags[0] = True
            new_state.cameras.active_sequence = 1
            return "", new_state
        
        self.register("LCS01", handle_lcs01)
        
        def handle_lcs02(state: DeviceState) -> Tuple[str, DeviceState]:
            """LCS02: Trigger light-camera sequence 2."""
            new_state = state.copy()
            new_state.cameras.flags[1] = True
            new_state.cameras.active_sequence = 2
            return "", new_state
        
        self.register("LCS02", handle_lcs02)
        
        def handle_lcs03(state: DeviceState) -> Tuple[str, DeviceState]:
            """LCS03: Trigger light-camera sequence 3."""
            new_state = state.copy()
            new_state.cameras.flags[2] = True
            new_state.cameras.active_sequence = 3
            return "", new_state
        
        self.register("LCS03", handle_lcs03)
        
        def handle_lcstp(state: DeviceState) -> Tuple[str, DeviceState]:
            """LCStp: Trigger all light-camera sequences."""
            new_state = state.copy()
            for i in range(7):
                new_state.cameras.flags[i] = True
            new_state.cameras.active_sequence = -1  # All
            return "", new_state
        
        self.register("LCSTP", handle_lcstp)
        
        def handle_lcsbm(state: DeviceState) -> Tuple[str, DeviceState]:
            """LCSbm: Trigger bottom light-camera sequences."""
            new_state = state.copy()
            new_state.cameras.flags[3] = True
            new_state.cameras.flags[4] = True
            new_state.cameras.flags[5] = True
            new_state.cameras.active_sequence = 2  # Bottom
            return "", new_state
        
        self.register("LCSBM", handle_lcsbm)
        
        # ===== SENSOR POWER CONTROL =====
        def handle_pos01(state: DeviceState) -> Tuple[str, DeviceState]:
            """POS01: Power on sensor 1."""
            new_state = state.copy()
            new_state.sensor_top.powered = True
            return "", new_state
        
        self.register("POS01", handle_pos01)
        
        def handle_pos02(state: DeviceState) -> Tuple[str, DeviceState]:
            """POS02: Power on sensor 2."""
            new_state = state.copy()
            new_state.sensor_bottom.powered = True
            return "", new_state
        
        self.register("POS02", handle_pos02)
        
        def handle_pos03(state: DeviceState) -> Tuple[str, DeviceState]:
            """POS03: Power on sensor 3."""
            # Phase 1: Generic sensor power on
            return "", state
        
        self.register("POS03", handle_pos03)
        
        # ===== TOWER LAMPS =====
        def handle_tred1(state: DeviceState) -> Tuple[str, DeviceState]:
            """TRED1: Turn red tower lamp ON."""
            new_state = state.copy()
            new_state.lamps.red = True
            return "", new_state
        
        self.register("TRED1", handle_tred1)
        
        def handle_tred0(state: DeviceState) -> Tuple[str, DeviceState]:
            """TRED0: Turn red tower lamp OFF."""
            new_state = state.copy()
            new_state.lamps.red = False
            return "", new_state
        
        self.register("TRED0", handle_tred0)
        
        def handle_tyel1(state: DeviceState) -> Tuple[str, DeviceState]:
            """TYEL1: Turn yellow tower lamp ON."""
            new_state = state.copy()
            new_state.lamps.yellow = True
            return "", new_state
        
        self.register("TYEL1", handle_tyel1)
        
        def handle_tyel0(state: DeviceState) -> Tuple[str, DeviceState]:
            """TYEL0: Turn yellow tower lamp OFF."""
            new_state = state.copy()
            new_state.lamps.yellow = False
            return "", new_state
        
        self.register("TYEL0", handle_tyel0)
        
        def handle_tgrn1(state: DeviceState) -> Tuple[str, DeviceState]:
            """TGRN1: Turn green tower lamp ON."""
            new_state = state.copy()
            new_state.lamps.green = True
            return "", new_state
        
        self.register("TGRN1", handle_tgrn1)
        
        def handle_tgrn0(state: DeviceState) -> Tuple[str, DeviceState]:
            """TGRN0: Turn green tower lamp OFF."""
            new_state = state.copy()
            new_state.lamps.green = False
            return "", new_state
        
        self.register("TGRN0", handle_tgrn0)
        
        def handle_tbzr1(state: DeviceState) -> Tuple[str, DeviceState]:
            """TBZR1: Turn buzzer ON."""
            new_state = state.copy()
            new_state.lamps.buzzer = True
            return "", new_state
        
        self.register("TBZR1", handle_tbzr1)
        
        def handle_tbzr0(state: DeviceState) -> Tuple[str, DeviceState]:
            """TBZR0: Turn buzzer OFF."""
            new_state = state.copy()
            new_state.lamps.buzzer = False
            return "", new_state
        
        self.register("TBZR0", handle_tbzr0)
        
        # ===== HARDWARE BUTTON CONTROL =====
        def handle_atrun(state: DeviceState) -> Tuple[str, DeviceState]:
            """ATRUN: Attach/Enable RUN button interrupt."""
            return "", state
        
        self.register("ATRUN", handle_atrun)
        
        def handle_dtrun(state: DeviceState) -> Tuple[str, DeviceState]:
            """DTRUN: Detach/Disable RUN button interrupt."""
            return "", state
        
        self.register("DTRUN", handle_dtrun)
        
        def handle_atpau(state: DeviceState) -> Tuple[str, DeviceState]:
            """ATPAU: Attach/Enable PAUSE button interrupt."""
            return "", state
        
        self.register("ATPAU", handle_atpau)
        
        def handle_dtpau(state: DeviceState) -> Tuple[str, DeviceState]:
            """DTPAU: Detach/Disable PAUSE button interrupt."""
            return "", state
        
        self.register("DTPAU", handle_dtpau)
        
        def handle_atstp(state: DeviceState) -> Tuple[str, DeviceState]:
            """ATSTP: Attach/Enable STOP button interrupt."""
            return "", state
        
        self.register("ATSTP", handle_atstp)
        
        def handle_dtstp(state: DeviceState) -> Tuple[str, DeviceState]:
            """DTSTP: Detach/Disable STOP button interrupt."""
            return "", state
        
        self.register("DTSTP", handle_dtstp)
        
        def handle_atbof(state: DeviceState) -> Tuple[str, DeviceState]:
            """ATBOF: Attach/Enable BUZZER OFF button interrupt."""
            return "", state
        
        self.register("ATBOF", handle_atbof)
        
        def handle_dtbof(state: DeviceState) -> Tuple[str, DeviceState]:
            """DTBOF: Detach/Disable BUZZER OFF button interrupt."""
            return "", state
        
        self.register("DTBOF", handle_dtbof)
        
        # ===== SHUTDOWN =====
        def handle_tpstp(state: DeviceState) -> Tuple[str, DeviceState]:
            """tpSTP: Shutdown/Stop command."""
            return "", state
        
        self.register("tpSTP", handle_tpstp)
        
        def handle_tpstr(state: DeviceState) -> Tuple[str, DeviceState]:
            """tpSTR: Status/State response."""
            # This is a response opcode, not typically called
            return "TPSTR", state
        
        self.register("tpSTR", handle_tpstr)
        
        # ===== ADDITIONAL HANDLERS FOR COMPLETENESS =====
        def handle_rfs01(state: DeviceState) -> Tuple[str, DeviceState]:
            """RFS01: Reference search command."""
            return "TRD01", state  # Return "Done" response
        
        self.register("RFS01", handle_rfs01)
        
        def handle_dhbls(state: DeviceState) -> Tuple[str, DeviceState]:
            """DHBLS: Disable all hardware buttons and sensors."""
            new_state = state.copy()
            new_state.sensor_top.attached = False
            new_state.sensor_bottom.attached = False
            new_state.encoder_top.enabled = False
            new_state.encoder_bottom.enabled = False
            return "", new_state
        
        self.register("DHBLS", handle_dhbls)
        
        def handle_hwbdb(state: DeviceState) -> Tuple[str, DeviceState]:
            """HWBDB: Hardware button debug."""
            return "", state
        
        self.register("HWBDB", handle_hwbdb)
        
        # ===== ERROR HANDLING =====
        def handle_fls(state: DeviceState) -> Tuple[str, DeviceState]:
            """FLS: Failed/Error response (standard failure response)."""
            return "FLS", state
        
        self.register("FLS", handle_fls)
