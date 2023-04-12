q = int(input('q='))
for k in range(2, q+1):
    if q % k == 0:
        break

if k == q:
    print(q, 'is Prime')
else:
    print(q, '=', k, 'x', q//k)
    print(q, 'is not Prime')