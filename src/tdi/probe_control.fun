/*	 PROBE_CONTROL.FUN
; PURPOSE:	Return the control byte for Brian's
;               probe setup.  For use with the EDGE.PROBES...
;               subtree.
; CATEGORY:	CMOD
; CALLING SEQUENCE: PROBE_CONTROL(_supply_status, _supply_selection, _monitor_gain, _current_monitor, _mode)
;
; INPUTS:       name			node			value
;
; 		_supply_status :        DC_PLUS			"Grounded" | "Floating"
;		_supply_selection :     .PROBE:POWER_SUPPLY     "Sweep A" | "Sweep B" | "DC -" | "DC +"
;		_monitor_gain :		.PROBE:V_GAIN_SET	4.0 | 40.0
;		_current_monitor :      .PROBE:I_GAIN_SET       0.02 | 0.1 | 0.5 | 2.0
;		_mode :                 .PROBE:PROBE_MODE	"Floating" | "Current"
;
; OPTIONAL INPUT PARAMETERS: --
; KEYWORD PARAMETERS: --
; OUTPUTS:	--
; OPTIONAL OUTPUT PARAMETERS: --
; COMMON BLOCKS: --
; SIDE EFFECTS: --
; RESTRICTIONS: --
; PROCEDURE:	--
; MODIFICATION HISTORY:
;	JAS 15-SEP-1992 Initial coding.
*/
FUN PUBLIC PROBE_CONTROL(in _supply_status, in _supply_selection, in _monitor_gain, in _current_monitor, in _mode) {

  FUN PRIVATE SUPPLY_STATUS(IN _STAT) {
    SWITCH(_stat) {
      case ("Grounded") _ans = 1; break;
      case ("Floating") _ans = 0; break;
    };
    return(_ans);
  };

  FUN PRIVATE SUPPLY_SELECTION(in _selection) {
    SWITCH(_selection) {
      case ("Sweep A") _ans = 0; break;
      case ("Sweep B") _ans = 2; break;
      case ("DC -") _ans = 4; break;
      case ("DC +") _ans = 6; break;
    }
    return(_ans);
  };

  FUN PRIVATE MONITOR_GAIN(in _gain) {
    SWITCH(_gain) {
      case (40.0) _ans = 0; break;
      case (4.0) _ans = 8; break;
    }
    return(_ans);
  };

  FUN PRIVATE CURRENT_MONITOR(in _gain) {
    SWITCH(_gain) {
      case ( 0.0) _ans =  0; break;
      case ( 0.005) _ans = 16; break;
      case ( 0.02) _ans = 32; break;
      case ( 0.1) _ans = 48; break;
      case ( 0.5) _ans = 64; break;
      case ( 2.0) _ans = 80; break;
    }
    return (_ans);
  };

  FUN PRIVATE PROBE_MODE(in _selection) {
    SWITCH(_selection) {
      case ("Current") _ans = 0; break;
      case ("Floating") _ans = 128; break;
    }
    return(_ans);
  };

  return( SUPPLY_STATUS(_supply_status) | 
          SUPPLY_SELECTION(_supply_selection) | 
          MONITOR_GAIN(_monitor_gain) | 
          CURRENT_MONITOR(_current_monitor) |
          PROBE_MODE(_mode));
}
