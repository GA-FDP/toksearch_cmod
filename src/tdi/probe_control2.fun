/* PROBE_CONTROL2.FUN
; PURPOSE: Return the control byte for Brian's
;               probe setup.  For use with the EDGE.PROBES...
;               subtree.
; CATEGORY: CMOD
; CALLING SEQUENCE: PROBE_CONTROL2(_supply_status, _supply_selection, _monitor_gain, _current_monitor, _mode, _card_type)
;
; INPUTS:       name node value
;               _card_type              .PROBE:CARD_TYPE        "Langmuir" | "Grid"
;
;          if _card_type is "Langmuir" then do the same as before
; _supply_status :        DC_PLUS "Grounded" | "Floating"
; _supply_selection :     .PROBE:POWER_SUPPLY     "Sweep A" | "Sweep B" | "DC -" | "DC +"
; _monitor_gain : .PROBE:V_GAIN_SET 4.0 | 40.0
; _current_monitor :      .PROBE:I_GAIN_SET       0.005 | 0.02 | 0.1 | 0.5 | 2.0
; _mode :                 .PROBE:PROBE_MODE "Floating" | "Current"
;
;          if _card_type is "Grid" then 
; _supply_status :        DC_PLUS ignored, set SUPPLY_STATUS _ans=0
; _supply_selection :     .PROBE:POWER_SUPPLY     ignored, set SUPPY_SELECTION _ans=0
; _monitor_gain : .PROBE:V_GAIN_SET ignored, set MONITOR_GAIN _ans=0
; _current_monitor :      .PROBE:I_GAIN_SET                2.0E-3 | 5.0E-5 | 1.25E-6
;                                               set CURRENT_MONITOR _ans =         0    |   16     |   48
; _mode :                 .PROBE:PROBE_MODE    "Floating" | "Current"
;                                               set PROBE_MODE _ans =        128      |   0  
; _card_type:             .PROBE:CARD_TYPE        "Langmuir" | "Grid" 
*/
FUN PUBLIC PROBE_CONTROL2(in _supply_status, in _supply_selection, in _monitor_gain, in _current_monitor, in _mode, in _card_type) 
{

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

  FUN PRIVATE CURRENT_MONITOR_GRID(in _gain) {
    SWITCH(_gain) {
      case ( 1.25E-6) _ans =  0; break;
      case ( 5.E-5) _ans = 32; break;
      case ( 2.E-3) _ans = 48; break;
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

  _ans = 0;
  switch (_card_type) 
  {
    case ("Langmuir") _ans = 
                SUPPLY_STATUS(_supply_status) |
                SUPPLY_SELECTION(_supply_selection) |
                MONITOR_GAIN(_monitor_gain) |
                CURRENT_MONITOR(_current_monitor) |
                PROBE_MODE(_mode);
              break;
    case("Grid") _ans =  
                CURRENT_MONITOR_GRID(_current_monitor) | 
                PROBE_MODE(_mode) ;
              break;
    case("HCGrid") _ans =  
                PROBE_MODE(_mode) ;
              break;
  }
   return(_ans);
}
