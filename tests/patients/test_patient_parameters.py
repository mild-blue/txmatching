from kidney_exchange.patients.patient_parameters import PatientParameters

donor_parameters_Joe = PatientParameters(blood_group="A",
                                         hla_antigens=["A11", "A26", "B38", "B62", "DR4", "DR11", "DR52", "DR53", "DQ7",
                                                       "DQ8", "DP2", "DP10", "Cw9", "Cw12"])

recipient_parameters_Jack = PatientParameters(blood_group="A",
                                              acceptable_blood_groups=["A", "0"],
                                              hla_antigens=["A1", "A30", "B14", "B15", "B62", "B63", "B64", "B65",
                                                            "B75", "B76", "B77", "DR4", "DR11"],
                                              hla_antibodies=["A2", "A23", "A24", "A68", "A69", "Cw2", "Cw5", "Cw6",
                                                              "Cw7", "Cw17", "Cw18", "DQ2", "DP3", "DP6", "DP9", "DP14",
                                                              "DP17"])
