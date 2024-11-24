import math
import argparse

standardResistors = {
    12: [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2, 10],
    24: [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1, 10],
    96: [1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30,
         1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74,
         1.78, 1.82, 1.87 ,1.91, 1.96, 2.00, 2.05, 2.10 ,2.15, 2.21, 2.26, 2.32,
         2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09,
         3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
         4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49,
         5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32,
         7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76, 10.00]
}

resistorMapping = {
    1 : {"RTop": "R1", "RBot": "R2"},
    2 : {"RTop": "R3", "RBot": "R4"},
    3 : {"RTop": "R5", "RBot": "R6"},
    4 : {"RTop": "R7", "RBot": "R8"},
    5 : {"RTop": "R9", "RBot": "R10"},
    6 : {"RTop": "R11", "RBot": "R12"},
    7 : {"RTop": "R13", "RBot": "R14"},
    8 : {"RTop": "R15", "RBot": "R16"}
}

def resistorRound(args, val):
    if args.resistorAccuracy == 0 or val <= 0:
        return val
    logval = math.log10(val)
    Decade = int(math.floor(logval))
    fraction = logval - Decade
    Rnum = int(round(fraction * args.resistorAccuracy))
    if Rnum >= args.resistorAccuracy:
        Rnum -= args.resistorAccuracy
        Decade += 1
    normVal = standardResistors[args.resistorAccuracy][Rnum]
    return normVal * (10 ** Decade)

def f2rvalue(val):
    multipliers = ["u", "m", "R", "k", "M", "G", "T"]
    if val == 0:
        return "0"
    if val < 0:
        return "-??"
    powof10 = int(math.floor(math.log10(val) + 0.000000001))
    powof1000 = int(math.floor(powof10 / 3 + 0.000001))
    if powof10 < -6:
        return "~0"
    if powof10 > 13:
        return "inf"
    suffix = multipliers[powof1000 + 2]
    normval = val / (10 ** (powof1000 * 3))
    roundval = round(normval * 1000) / 1000
    return f"{roundval}{suffix}"

def RParr(r1, r2):
    if r1 + r2 == 0:
        return 0
    return (r1 * r2) / (r1 + r2)

def getStagePower(i):
    stageOrder = [1, 2, 3, 4, 5, 6, 7, 8]
    stageRank = stageOrder[i - 1]
    return 2 ** (stageRank - 1)

def calculate(args):
    attenuationRatio = 10 ** (-0.05 * args.attenuationSteps)
    RTopNominal = [0]*12  # Extended size to accommodate args.stages+1
    RBotNominal = [0]*12
    RTopRounded = [0]*12
    RBotRounded = [0]*12
    MaxInRes = [0]*12
    MinInRes = [0]*12
    MaxOutRes = [0]*12
    MinOutRes = [0]*12
    minAtt = [0]*12
    maxAtt = [0]*12
    # Prepare data storage for the table
    table_data = []
    # set nominal and rounded resistor values
    for i in range(1, args.stages+1):
        stagePower = getStagePower(i)
        AttenuationRatioNominal = attenuationRatio ** stagePower

        # Avoid underflow by setting a minimum value
        AttenuationRatioNominal = max(AttenuationRatioNominal, 1e-12)

        if args.attenuatorType == 0:
            # const input
            RTopNominal[i] = args.resistance * (1 - AttenuationRatioNominal)
            denominator = (1 / AttenuationRatioNominal - 1)
            # Avoid division by zero
            denominator = max(denominator, 1e-12)
            RBotNominal[i] = args.resistance / denominator
        else:
            # const output
            if i == 1:
                RTopNominal[i] = args.resistance / AttenuationRatioNominal
            else:
                RTopNominal[i] = args.resistance * (1 - AttenuationRatioNominal) / AttenuationRatioNominal
            denominator = (1 - AttenuationRatioNominal)
            # Avoid division by zero
            denominator = max(denominator, 1e-12)
            RBotNominal[i] = args.resistance / denominator

        RTopRounded[i] = resistorRound(args, RTopNominal[i])
        RBotRounded[i] = resistorRound(args, RBotNominal[i])
        nominal_att = args.attenuationSteps * stagePower
        # Collect data for the table
        table_data.append({
            'Stage': i,
            'RTop': f2rvalue(RTopRounded[i]),
            'RBot': f2rvalue(RBotRounded[i]),
            'RTopNom': f2rvalue(RTopNominal[i]),
            'RBotNom': f2rvalue(RBotNominal[i]),
            'Nominal_Attenuation': f"{nominal_att} dB"
        })

    # Set final load resistor (include the last resistor in the ladder)
    if args.attenuatorType == 0:
        RTopRounded[args.stages+1] = 0
        RBotRounded[args.stages+1] = resistorRound(args, args.resistance)
        switchedRes = args.resistance
        final_load_resistor = f2rvalue(RBotRounded[args.stages+1])
    else:
        RTopRounded[args.stages+1] = 0
        RBotRounded[args.stages+1] = resistorRound(args, args.resistance * 100)  # Just high
        switchedRes = 0
        final_load_resistor = f2rvalue(RBotRounded[args.stages+1])

    cumulativeAtt_dB = 0.0
    MinInRes[args.stages+1] = RBotRounded[args.stages+1]
    MaxInRes[args.stages+1] = RBotRounded[args.stages+1]
    MinOutRes[0] = 0
    MaxOutRes[0] = 0
    switchedRes = args.resistance if args.attenuatorType == 0 else 0

    for i in range(args.stages, 0, -1):
        if args.attenuatorType == 0:
            rp = RParr(RBotRounded[i], switchedRes)
            switchedRes = RTopRounded[i] + rp
            # Avoid division by zero
            if switchedRes == 0:
                switchedGain = 0
            else:
                switchedGain = rp / switchedRes
            # Convert gain to dB and add to cumulative attenuation
            if switchedGain > 0:
                cumulativeAtt_dB += 20 * math.log10(switchedGain)
            else:
                cumulativeAtt_dB += -200  # Large attenuation
        MinInRes[i] = min(MinInRes[i+1], RTopRounded[i] + RParr(RBotRounded[i], MinInRes[i+1]))
        MaxInRes[i] = max(MaxInRes[i+1], RTopRounded[i] + RParr(RBotRounded[i], MaxInRes[i+1]))

    for i in range(1, args.stages+1):
        if i == 1 and args.attenuatorType != 0:
            MinOutRes[1] = RParr(RTopRounded[1], RBotRounded[1])
            MaxOutRes[1] = MinOutRes[1]
            switchedRes = MinOutRes[1]
            denominator = RTopRounded[1] + RBotRounded[1]
            if denominator == 0:
                switchedGain = 0
            else:
                switchedGain = RBotRounded[1] / denominator
            if switchedGain > 0:
                cumulativeAtt_dB += 20 * math.log10(switchedGain)
            else:
                cumulativeAtt_dB += -200  # Large attenuation
        else:
            MinOutRes[i] = min(MinOutRes[i-1], RParr(MinOutRes[i-1] + RTopRounded[i], RBotRounded[i]))
            MaxOutRes[i] = max(MaxOutRes[i-1], RParr(MaxOutRes[i-1] + RTopRounded[i], RBotRounded[i]))
            if args.attenuatorType != 0:
                denominator = RTopRounded[i] + RBotRounded[i] + switchedRes
                if denominator == 0:
                    switchedGain = 0
                else:
                    switchedGain = RBotRounded[i] / denominator
                switchedRes = RParr(switchedRes + RTopRounded[i], RBotRounded[i])
                if switchedGain > 0:
                    cumulativeAtt_dB += 20 * math.log10(switchedGain)
                else:
                    cumulativeAtt_dB += -200  # Large attenuation

    fullAtt = cumulativeAtt_dB
    AvgStepSize = -1.0 * fullAtt / (2 ** args.stages - 1)
    fullAtt = round(fullAtt * 10) / 10

    min_input_res = f2rvalue(MinInRes[1])
    max_input_res = f2rvalue(MaxInRes[1])
    min_output_res = f2rvalue(MinOutRes[args.stages])
    max_output_res = f2rvalue(MaxOutRes[args.stages])
    num_positions = 2 ** args.stages
    total_att = fullAtt
    step_size = round(AvgStepSize * 1000) / 1000

    # Calculate attenuation errors per stage
    for idx, data in enumerate(table_data):
        i = idx + 1
        linearizedStageAtt = AvgStepSize * getStagePower(i)
        if args.attenuatorType == 0:
            minRes = RParr(MinInRes[i+1], RBotRounded[i])
            maxRes = RParr(MaxInRes[i+1], RBotRounded[i])
            denominator_min = RTopRounded[i] + minRes
            denominator_max = RTopRounded[i] + maxRes
            if denominator_min > 0:
                maxAtt_i = 20 * math.log10(minRes / denominator_min)
            else:
                maxAtt_i = -200
            if denominator_max > 0:
                minAtt_i = 20 * math.log10(maxRes / denominator_max)
            else:
                minAtt_i = -200
        else:
            minRes = MinOutRes[i-1] + RTopRounded[i]
            maxRes = MaxOutRes[i-1] + RTopRounded[i]
            denominator_min = RBotRounded[i] + minRes
            denominator_max = RBotRounded[i] + maxRes
            if denominator_max > 0:
                maxAtt_i = 20 * math.log10(RBotRounded[i] / denominator_max)
            else:
                maxAtt_i = -200
            if denominator_min > 0:
                minAtt_i = 20 * math.log10(RBotRounded[i] / denominator_min)
            else:
                minAtt_i = -200

        errAtt = maxAtt_i + linearizedStageAtt
        if abs(errAtt) < abs(minAtt_i + linearizedStageAtt):
            errAtt = minAtt_i + linearizedStageAtt
        errAtt = round(errAtt * 100) / 100
        # Add attenuation error to the data
        data['Attenuation_Error'] = f"{errAtt} dB"

    # Now, format and print the table
    print("\nAttenuator Design Calculation Results:")
    print("=" * 130)
    # Header
    header = f"| {'Resistor Stage':^14} | {'A (common)':^16} | {'B (common)':^16} | {'A (nominal)':^16} | {'B (nominal)':^16} | {'Attenuation':^12} | {'Attenuation Error':^18} |"
    print(header)
    print("-" * 130)
    # Data rows
    for data in table_data:
        rtop_info = "{} ({})".format(data['RTop'], resistorMapping[data['Stage']]['RTop'])
        rbot_info = "{} ({})".format(data['RBot'], resistorMapping[data['Stage']]['RBot'])
        row = f"| {data['Stage']:^14} | {rtop_info:^16} | {rbot_info:^16} | {data['RTopNom']:^16} | {data['RBotNom']:^16} | {data['Nominal_Attenuation']:^12} | {data['Attenuation_Error']:^18} |"
        print(row)
    print("=" * 130)
    # Summary
    print(f"Final Load Resistor (Rout): {final_load_resistor}")
    print(f"Minimum Input Resistance: {min_input_res}")
    print(f"Maximum Input Resistance: {max_input_res}")
    print(f"Minimum Output Resistance: {min_output_res}")
    print(f"Maximum Output Resistance: {max_output_res}")
    print(f"Attenuator Maximum Attenuation: {total_att} dB")
    print(f"Number of Attenuator Positions: {num_positions}")
    print(f"Attenuator Step Size: {step_size} dB")

def main():
    parser = argparse.ArgumentParser(description='Attenuator Design Calculator')
    parser.add_argument('--stages', type=int, default=8, help='Number of stages (default: 8)')
    parser.add_argument('--resistorAccuracy', type=int, choices=[0, 12, 24, 96], default=96, help='E-Series (0,12,24,96; default: 96)')
    parser.add_argument('--attenuatorType', type=int, choices=[0,1], default=0, help='Attenuator type (default: 0): 0 (constant input) In a conventional analog potentiometer, the input resistance is constant: this is the value of the resistance between both end points. Its output resistance varies with the position of the sliding contact: when the contact is near either end the output resistance aproaches zero, and somewhere in between the output resistance reaches a maximum of 1/4 of the input resistance. This behavior somewhat resembles the constant input resistance stepped attenuator: the output resistance varies with the selected attenuation. However, the relation between attenuation-level and output-resistance is significantly more complex: a high attenuation (low output signal) does not imply a low output resistance. This attenuator type requires a final load resistance that is identical to the input resistance of each stage, which is included in above design.\nThe alternative design option provides a constant output resistance over all attenuation levels, but has a variable input resistance. Its first stage is configured slightly differently to establish the selected output resistance. A final load resistance can cause extra attenuation which is not accounted for in above numbers. Note that the uniformity of the attenuation-steps remains correct even if the applied load resistance would be chosen relatively low.')
    parser.add_argument('--resistance', type=float, default=10000, help='Stage constant resistance in ohms (default: 10000)')
    parser.add_argument('--attenuationSteps', type=float, default=0.5, help='Stage attenuation in dB (default: 0.5)')
    args = parser.parse_args()
    calculate(args)

if __name__ == "__main__":
    main()