
! a + b = c
subroutine add(a, b, c)
  
  use some_module, only: something

  implicit none
  integer,    intent(in) :: a
  integer,    intent(in) :: b
  integer, intent(inout) :: c

  c = a + b

end subroutine add

! a - b = c
subroutine sub(a, b, c)
  
  use some_module, only: something

  implicit none
  integer,    intent(in) :: a
  integer,    intent(in) :: b
  integer, intent(inout) :: c

  c = a - b

end subroutine sub
