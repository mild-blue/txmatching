from txmatching.utils.hla_system.hla_preparation_utils import create_antibody

TYPE_A_EXAMPLE_REC = [create_antibody('A*01:01', 63, 4000),
                      create_antibody('A*02:01', 15721, 4000),
                      create_antibody('A*02:02', 14335, 4000),
                      create_antibody('A*02:03', 14169, 4000),
                      create_antibody('A*02:05', 17078, 4000),
                      create_antibody('A*03:01', 8405, 4000),
                      create_antibody('A*11:01', 19740, 4000),
                      create_antibody('A*11:02', 19723, 4000),
                      create_antibody('A*23:01', 361, 4000),
                      create_antibody('A*24:02', 14, 4000),
                      create_antibody('A*24:03', 10361, 4000),
                      create_antibody('A*25:01', 9769, 4000),
                      create_antibody('A*26:01', 7353, 4000),
                      create_antibody('A*29:01', 13753, 4000),
                      create_antibody('A*29:02', 17961, 4000),
                      create_antibody('A*30:01', 7633, 4000),
                      create_antibody('A*31:01', 7055, 4000),
                      create_antibody('A*32:01', 13535, 4000),
                      create_antibody('A*33:01', 10015, 4000),
                      create_antibody('A*33:03', 6503, 4000),
                      create_antibody('A*34:02', 10480, 4000),
                      create_antibody('A*36:01', 8336, 4000),
                      create_antibody('A*43:01', 13551, 4000),
                      create_antibody('A*66:01', 10919, 4000),
                      create_antibody('A*66:02', 17012, 4000),
                      create_antibody('A*68:01', 11895, 4000),
                      create_antibody('A*68:02', 11927, 4000),
                      create_antibody('A*69:01', 11673, 4000),
                      create_antibody('A*74:01', 8745, 4000),
                      create_antibody('A*80:01', 42, 4000),
                      create_antibody('B*07:02', 20215, 4000),
                      create_antibody('B*07:03', 19384, 4000),
                      create_antibody('B*08:01', 15993, 4000),
                      create_antibody('B*13:02', 77, 4000),
                      create_antibody('B*14:01', 6456, 4000),
                      create_antibody('B*14:02', 3721, 4000),
                      create_antibody('B*15:01', 9257, 4000),
                      create_antibody('B*15:02', 2337, 4000),
                      create_antibody('B*15:03', 4921, 4000),
                      create_antibody('B*15:12', 51, 4000),
                      create_antibody('B*15:13', 1516, 4000),
                      create_antibody('B*15:16', 9878, 4000),
                      create_antibody('B*15:18', 7358, 4000),
                      create_antibody('B*18:01', 6421, 4000),
                      create_antibody('B*27:03', 6497, 4000),
                      create_antibody('B*27:05', 9305, 4000),
                      create_antibody('B*27:08', 17497, 4000),
                      create_antibody('B*35:01', 67, 4000),
                      create_antibody('B*35:08', 26, 4000),
                      create_antibody('B*37:01', 13959, 4000),
                      create_antibody('B*38:01', 5819, 4000),
                      create_antibody('B*39:01', 9032, 4000),
                      create_antibody('B*40:01', 19866, 4000),
                      create_antibody('B*40:02', 12539, 4000),
                      create_antibody('B*41:01', 16811, 4000),
                      create_antibody('B*42:01', 19628, 4000),
                      create_antibody('B*44:02', 840, 4000),
                      create_antibody('B*44:03', 1428, 4000),
                      create_antibody('B*45:01', 829, 4000),
                      create_antibody('B*46:01', 3021, 4000),
                      create_antibody('B*47:01', 2932, 4000),
                      create_antibody('B*48:01', 12753, 4000),
                      create_antibody('B*49:01', 6956, 4000),
                      create_antibody('B*50:01', 5226, 4000),
                      create_antibody('B*51:01', 327, 4000),
                      create_antibody('B*52:01', 1431, 4000),
                      create_antibody('B*53:01', 37, 4000),
                      create_antibody('B*54:01', 19428, 4000),
                      create_antibody('B*55:01', 20355, 4000),
                      create_antibody('B*56:01', 19883, 4000),
                      create_antibody('B*57:01', 1522, 4000),
                      create_antibody('B*58:01', 737, 4000),
                      create_antibody('B*59:01', 17033, 4000),
                      create_antibody('B*67:01', 20560, 4000),
                      create_antibody('B*73:01', 6619, 4000),
                      create_antibody('B*78:01', 1702, 4000),
                      create_antibody('B*81:01', 20380, 4000),
                      create_antibody('B*82:02', 18871, 4000),
                      create_antibody('C*01:02', 1768, 4000),
                      create_antibody('C*02:02', 120, 4000),
                      create_antibody('C*03:03', 678, 4000),
                      create_antibody('C*03:04', 482, 4000),
                      create_antibody('C*04:01', 93, 4000),
                      create_antibody('C*04:03', 131, 4000),
                      create_antibody('C*05:01', 349, 4000),
                      create_antibody('C*06:02', 445, 4000),
                      create_antibody('C*07:01', 1097, 4000),
                      create_antibody('C*07:02', 1415, 4000),
                      create_antibody('C*08:01', 3168, 4000),
                      create_antibody('C*08:02', 2008, 4000),
                      create_antibody('C*12:02', 2310, 4000),
                      create_antibody('C*14:02', 3025, 4000),
                      create_antibody('C*15:02', 1447, 4000),
                      create_antibody('C*16:01', 646, 4000),
                      create_antibody('C*17:01', 838, 4000),
                      create_antibody('C*18:01', 367, 4000),
                      create_antibody('DP[01:03,01:01]', 201, 4000),
                      create_antibody('DP[01:03,03:01]', 242, 4000),
                      create_antibody('DP[01:03,04:02]', 110, 4000),
                      create_antibody('DP[01:03,06:01]', 150, 4000),
                      create_antibody('DP[01:03,18:01]', 118, 4000),
                      create_antibody('DP[02:01,01:01]', 1488, 4000),
                      create_antibody('DP[02:01,04:01]', 1293, 4000),
                      create_antibody('DP[02:01,05:01]', 1462, 4000),
                      create_antibody('DP[02:01,09:01]', 1157, 4000),
                      create_antibody('DP[02:01,11:01]', 1448, 4000),
                      create_antibody('DP[02:01,13:01]', 1450, 4000),
                      create_antibody('DP[02:01,14:01]', 1217, 4000),
                      create_antibody('DP[02:01,15:01]', 1078, 4000),
                      create_antibody('DP[02:01,17:01]', 1120, 4000),
                      create_antibody('DP[02:01,19:01]', 1304, 4000),
                      create_antibody('DP[02:02,01:01]', 1401, 4000),
                      create_antibody('DP[02:02,04:01]', 1345, 4000),
                      create_antibody('DP[02:02,05:01]', 1414, 4000),
                      create_antibody('DP[02:02,28:01]', 1358, 4000),
                      create_antibody('DP[03:01,01:01]', 170, 4000),
                      create_antibody('DP[03:01,04:01]', 77, 4000),
                      create_antibody('DP[03:01,04:02]', 180, 4000),
                      create_antibody('DP[03:01,05:01]', 172, 4000),
                      create_antibody('DP[04:01,04:01]', 1018, 4000),
                      create_antibody('DP[04:01,13:01]', 1256, 4000),
                      create_antibody('DPA1*01:03', 59, 4000),
                      create_antibody('DPB1*02:01', 59, 4000),
                      create_antibody('DPB1*04:01', 59, 4000),
                      create_antibody('DQ[01:01,05:01]', 346, 4000),
                      create_antibody('DQ[01:02,05:01]', 252, 4000),
                      create_antibody('DQ[01:02,05:02]', 281, 4000),
                      create_antibody('DQ[01:02,06:02]', 171, 4000),
                      create_antibody('DQ[01:02,06:04]', 662, 4000),
                      create_antibody('DQ[01:03,06:01]', 52, 4000),
                      create_antibody('DQ[01:03,06:03]', 208, 4000),
                      create_antibody('DQ[01:04,05:03]', 156, 4000),
                      create_antibody('DQ[01:04,06:01]', 163, 4000),
                      create_antibody('DQ[02:01,02:01]', 154, 4000),
                      create_antibody('DQ[02:01,02:02]', 205, 4000),
                      create_antibody('DQ[02:01,03:02]', 512, 4000),
                      create_antibody('DQ[02:01,04:01]', 1069, 4000),
                      create_antibody('DQ[02:01,06:01]', 229, 4000),
                      create_antibody('DQ[03:01,03:01]', 253, 4000),
                      create_antibody('DQ[03:01,03:02]', 38, 4000),
                      create_antibody('DQ[03:01,04:02]', 439, 4000),
                      create_antibody('DQ[03:02,02:02]', 115, 4000),
                      create_antibody('DQ[03:02,03:01]', 298, 4000),
                      create_antibody('DQ[03:02,03:02]', 75, 4000),
                      create_antibody('DQ[03:02,03:03]', 254, 4000),
                      create_antibody('DQ[04:01,03:03]', 729, 4000),
                      create_antibody('DQ[04:01,04:01]', 521, 4000),
                      create_antibody('DQ[04:01,04:02]', 931, 4000),
                      create_antibody('DQ[05:01,03:01]', 447, 4000),
                      create_antibody('DQ[05:01,04:01]', 612, 4000),
                      create_antibody('DQ[06:01,03:01]', 345, 4000),
                      create_antibody('DQ[06:01,03:03]', 372, 4000),
                      create_antibody('DQ[06:01,04:02]', 535, 4000),
                      create_antibody('DQA1*05:01', 140, 4000),
                      create_antibody('DQB1*02:01', 140, 4000),
                      create_antibody('DQB1*02:02', 140, 4000),
                      create_antibody('DRB1*01:01', 243, 4000),
                      create_antibody('DRB1*01:02', 52, 4000),
                      create_antibody('DRB1*01:03', 186, 4000),
                      create_antibody('DRB1*03:01', 233, 4000),
                      create_antibody('DRB1*03:02', 271, 4000),
                      create_antibody('DRB1*03:03', 163, 4000),
                      create_antibody('DRB1*04:01', 169, 4000),
                      create_antibody('DRB1*04:02', 90, 4000),
                      create_antibody('DRB1*04:03', 149, 4000),
                      create_antibody('DRB1*04:04', 149, 4000),
                      create_antibody('DRB1*04:05', 112, 4000),
                      create_antibody('DRB1*07:01', 280, 4000),
                      create_antibody('DRB1*08:01', 75, 4000),
                      create_antibody('DRB1*08:02', 120, 4000),
                      create_antibody('DRB1*09:01', 350, 4000),
                      create_antibody('DRB1*10:01', 106, 4000),
                      create_antibody('DRB1*11:01', 211, 4000),
                      create_antibody('DRB1*11:03', 199, 4000),
                      create_antibody('DRB1*11:04', 137, 4000),
                      create_antibody('DRB1*12:01', 81, 4000),
                      create_antibody('DRB1*12:02', 137, 4000),
                      create_antibody('DRB1*13:01', 139, 4000),
                      create_antibody('DRB1*13:03', 120, 4000),
                      create_antibody('DRB1*13:05', 193, 4000),
                      create_antibody('DRB1*14:01', 101, 4000),
                      create_antibody('DRB1*14:03', 157, 4000),
                      create_antibody('DRB1*14:04', 176, 4000),
                      create_antibody('DRB1*15:01', 89, 4000),
                      create_antibody('DRB1*15:02', 209, 4000),
                      create_antibody('DRB1*15:03', 63, 4000),
                      create_antibody('DRB1*16:01', 152, 4000),
                      create_antibody('DRB1*16:02', 116, 4000),
                      create_antibody('DRB5*01:01', 172, 4000),
                      create_antibody('DRB5*02:02', 102, 4000),
                      create_antibody('DRB3*01:01', 124, 4000),
                      create_antibody('DRB3*02:02', 330, 4000),
                      create_antibody('DRB3*03:01', 96, 4000),
                      create_antibody('DRB4*01:01', 75, 4000)
                      ]
