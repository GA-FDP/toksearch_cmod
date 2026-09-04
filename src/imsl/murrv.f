      subroutine murrv(NRA, NCA, A, LDA, NX, X, IPATH, NY, Y)
C
C Emulation of IMSL routine MURRV
C
c$$$ Purpose:    Multiply a real rectangular matrix by a vector.
c$$$
c$$$   Usage:      CALL MURRV (NRA, NCA, A, LDA, NX, X, IPATH, NY, Y)
c$$$
c$$$   Arguments:
c$$$      NRA    - Number of rows of A.  (Input)
c$$$      NCA    - Number of columns of A.  (Input)
c$$$      A      - Real NRA by NCA matrix in full storage mode.  (Input)
c$$$      LDA    - Leading dimension of A exactly as specified in the
c$$$               dimension statement of the calling program.  (Input)
c$$$      NX     - Length of the vector X.  (Input)
c$$$               NX must be equal to NCA if IPATH is equal to 1.
c$$$               NX must be equal to NRA if IPATH is equal to 2.
c$$$      X      - Real vector of length NX.  (Input)
c$$$      IPATH  - Integer flag.  (Input)
c$$$               IPATH = 1 means the product Y = A*X is computed.
c$$$               IPATH = 2 means the product Y = trans(A)*X is computed
c$$$               where trans(A) is the transpose of A.
c$$$      NY     - Length of the vector Y.  (Input)
c$$$               NY must be equal to NRA if IPATH is equal to 1.
c$$$               NY must be equal to NCA if IPATH is equal to 2.
c$$$      Y      - Real vector of length NY containing the product A*X if
c$$$               IPATH is equal to 1 and the product trans(A)*X if IPATH
c$$$               is equal to 2.  (Output)
c$$$
c     Method: 
c           Brute Force, no optimization for storage order, no nothing
c           Just multiply them out in a nested do loop
c    Created 10/17/2002 - smw
c    10/18/2002 - Modify ipath=1 calculation for storage order efficiency
c
      integer nra,nca,lda,nx,ny,ipath
      real a(lda,nca),x(nx),y(ny)
      if (ipath.eq.1) then 
         if ((nx.ne.nca).or.(ny.ne.nra)) return
         do j=1,nra
            y(j)=0.
         enddo
         do k=1,nca
            do j=1,nra
               y(j)=y(j)+a(j,k)*x(k)
            enddo
         enddo
      else
         if(ipath.ne.2) return
         if((nx.ne.nra).or.(ny.ne.nca)) return
         do j=1,nca
            y(j)=0.
            do k=1,nra
               y(j)=y(j)+a(k,j)*x(k)
            enddo
         enddo
      endif
      return
      end

