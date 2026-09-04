      function get_input_p_to_v(name,struct)
c
c     Interface routine to pass C-style null-terminated strings 
c     to the get_input_p_to_v function. This kludge is necessary
c     in order to use character*(*) dummy inputs in that
c     function and things it calls
c
c     This routine must be compiled -fno-underscoring. 
c     Also, in order for the UPPERCASE form of the routine name,
c     as specified in the HYBRID tree, to work, an entry point
c     GET_INPUT_P_TO_V must be specified using the -defsym switch to ld. 
c
c Arguments:
c     name,struct    Intent IN   Null-terminated strings of maximum 
c                                length 255 characters. For a 
c                                description, see function get_input_p_to_v 
c                                in file hybrid_get_p_to_v.f
c
c Procedure:
c     The strings are scanned for the first null (char(0))
c     The resulting lengths are then passed by value, using %val,
c     as trailing arguments to the "real" get_input_p_to_v__ routine. 
c     Note that these trailing arguments are not explicitly present in 
c     either routine. Apparently, this is how Unix fortran (at least g77)
c     deals with string arguments. 
c     
c Revisions:
c     4/9/2002     Created - smw
c     9/2/2011     Modified to use integer(kind=7) for 
c                  multi-platform support -smw
c
      character*255 name,struct
      integer(kind=8) get_input_p_to_v, get_input_p_to_v_
c
      lname=0
      do i=1,len(name)
         if (name(i:i) .eq. char(0)) go to 10
         lname=lname+1
      enddo
 10   lstr=0
      do i=1,len(struct)
         if (struct(i:i) .eq. char(0)) go to 20
         lstr=lstr+1
      enddo
 20   continue
      get_input_p_to_v=get_input_p_to_v_(name,struct,%val(lname),
     $     %val(lstr))
      return
      end
