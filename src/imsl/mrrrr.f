      subroutine mrrrr(NRA, NCA, A, LDA, NRB, NCB, B, LDB,
     +                 NRC, NCC, C, LDC)
c Emulation for IMSL routine MRRRR
c$$$ Purpose:    Multiply two real rectangular matrices, A*B.
c$$$
c$$$   Usage:      CALL MRRRR (NRA, NCA, A, LDA, NRB, NCB, B, LDB,
c$$$                           NRC, NCC, C, LDC)
c$$$
c$$$   Arguments:
c$$$      NRA    - Number of rows of A.  (Input)
c$$$      NCA    - Number of columns of A.  (Input)
c$$$      A      - Real NRA by NCA matrix in full storage mode.  (Input)
c$$$      LDA    - Leading dimension of A exactly as specified in the
c$$$               dimension statement of the calling program.  (Input)
c$$$      NRB    - Number of rows of B.  (Input)
c$$$               NRB must be equal to NCA.
c$$$      NCB    - Number of columns of B.  (Input)
c$$$      B      - Real NRB by NCB matrix in full storage mode.  (Input)
c$$$      LDB    - Leading dimension of B exactly as specified in the
c$$$               dimension statement of the calling program.  (Input)
c$$$      NRC    - Number of rows of C.  (Input)
c$$$               NRC must be equal to NRA.
c$$$      NCC    - Number of columns of C.  (Input)
c$$$               NCC must be equal to NCB.
c$$$      C      - Real NRC by NCC matrix containing the product A*B in full
c$$$               storage mode.  (Output)
c$$$      LDC    - Leading dimension of C exactly as specified in the
c$$$               dimension statement of the calling program.  (Input)
c$$$
c
c Method: Brute force, just multiply in a nested do loop
c
c Revisions:
c     Created 10/17/2002  - smw
c
      integer nra,nca,lda,nrb,ncb,ldb,nrc,ncc,ldc
      real a(lda,nca),b(ldb,ncb),c(ldc,ncc)
      if ((nrb.ne.nca).or.(nrc.ne.nra).or.(ncc.ne.ncb)) return
      do i=1,nra
         do j=1,ncc
            c(i,j) = 0.
            do k=1,nrb
               c(i,j)=c(i,j)+a(i,k)*b(k,j)
            enddo
         enddo
      enddo
      return
      end
            
