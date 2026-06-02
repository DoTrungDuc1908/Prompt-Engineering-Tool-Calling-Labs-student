---
name: math_calc
track: extra
kind: local_formatter
provider: sympy
requires_env: []
inputs: [expression]
outputs: [items]
side_effect: false
---
# math_calc

Tính toán biểu thức toán học. Dùng sympy nếu có, fallback eval nếu không.
