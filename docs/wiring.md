# GPIO Wiring — Safe Bend Vision

## LED Pin Map (BCM Numbering)

| Side | Color  | BCM Pin | Physical Pin |
|------|--------|---------|--------------|
| A    | Red    | 17      | 11           |
| A    | Green  | 27      | 13           |
| A    | Blue   | 22      | 15           |
| B    | Red    | 5       | 29           |
| B    | Green  | 6       | 31           |
| B    | Blue   | 13      | 33           |

## LED Logic

| State        | GPIO Output         | Meaning                    |
|-------------|---------------------|----------------------------|
| Clear       | Green ON            | No vehicle detected        |
| Vehicle Far | Red + Green ON (Yellow) | Vehicle detected, low risk |
| Danger      | Red ON              | Vehicle close, high risk   |
| Error/Boot  | Blue ON             | Camera fault / initialising|

## Notes
- All LEDs are 12V — use appropriate transistor/relay driver circuit.
- Each LED connects via resistor to the GPIO pin through a driver (e.g. NPN transistor BC547).
- GPIO GND → common GND with LED driver circuit.
