1. Shot List ID – the number following the # symbol (e.g., 21). Use shot_id as the key.
2. Date – the full date shown at the top (e.g., June 27, 2025), and convert it to YYYYMMDD format (e.g., 20250627). Use date as the key.
3. Distance to Pin – the number in yards under the DISTANCE TO PIN label (e.g., 48). Use distance_to_pin as the key.
4. Carry – the number in yards under the CARRY label (e.g., 37.2). Use carry as the key.
5. From Pin - the number in feet between Distance to Pin and Carry (e.g., 31). Use from_pin as the key.
6. Extract the STROKES GAINED value that appears beneath FROM PIN in the left metrics column, not from the strokes gained box on the right summary panel.(e.g., -0.82, +0.22). Use sg_individual as the key and return as a numeric value (float), not a string.
7. Yardage Range – the label under the STROKES GAINED box on the right panel, below the "ALL" section (e.g., 30-50). Use yardage_range as the key.
8. From Yardage – extract the lower bound of the yardage range (e.g., 30 from 30-50). Use yardage_from as the key.
9. To Yardage – extract the upper bound of the yardage range (e.g., 50 from 30-50). Use yardage_to as the key.

