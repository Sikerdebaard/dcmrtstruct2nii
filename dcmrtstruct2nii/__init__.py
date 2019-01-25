from .facade.dcmrtstruct2nii import list_rt_structs, dcmrtstruct2nii

__all__ = [list_rt_structs, dcmrtstruct2nii]

# import math
#
# def test(xyz, delta = 0.0001):
#     orientation = ''
#
#     orientation_x = 'R' if xyz[0] < 0 else 'L'
#     orientation_y = 'A' if xyz[1] < 0 else 'P'
#     orientation_z = 'F' if xyz[2] < 0 else 'H'
#
#     abs_x = math.fabs(xyz[0])
#     abs_y = math.fabs(xyz[1])
#     abs_z = math.fabs(xyz[2])
#
#     for i in range(0, 3):
#         if abs_x > delta and abs_x > abs_y and abs_x > abs_z:
#             orientation += orientation_x
#             abs_x = 0
#         elif abs_y > delta and abs_y > abs_x and abs_y > abs_z:
#             orientation += orientation_y
#             abs_y = 0
#         elif abs_z > delta and abs_z > abs_x and abs_z > abs_y:
#             orientation += orientation_z
#             abs_z = 0
#         else:
#             break
#
#     return orientation
