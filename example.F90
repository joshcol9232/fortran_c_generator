
! a + b = c
subroutine add(add_a, add_b, add_c)
  
  use some_module, only: something

  implicit none
  integer,    intent(in) :: add_a
  integer,    intent(in) :: add_b
  integer, intent(inout) :: add_c

  add_c = add_a + add_b

end subroutine add

! a - b = c
subroutine sub(sub_a, sub_b, sub_c)
  
  use some_module, only: something

  implicit none
  integer,    intent(in) :: sub_a
  integer,    intent(in) :: sub_b
  integer, intent(out) :: sub_c

  sub_c = sub_a - sub_b

end subroutine sub


subroutine add_arrays(a, b, c)
  
  implicit none
  integer,    intent(in) :: a(:)
  integer,    intent(in) :: b(:)
  integer, intent(inout) :: c(222)

  c = a + b

end subroutine add_arrays

subroutine custom_type(self)

  implicit none
  type(a_custom_type), intent(inout) :: self
  
  call do_something_with_type(self)

end subroutine custom_type

