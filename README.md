# PatchOversamplingV2
Patch Oversampling (Synthesis) with Direct Patch Analysis

'''
    Patch Oversampling (Synthesis) with Direct Patch Analysis.
    Developer: Shu Wang
    Date: 2020-09-22
    Version: S2020.09.22 (Version 1.0)
    File Structure:
    PatchClearance
        |-- data                    # original patch folder.
            |-- negatives           # negative patches.
            |-- positives           # positive patches.
            |-- security_patch      # positive patches from NVD.
        |-- synthesis               # synthetic patch folder.
            |-- negatives           # corresponding synthetic negative patches.
            |-- positives           # corresponding synthetic positive patches.
            |-- security_patch      # corresponding synthetic positive NVD patches.
        |-- patch_oversampling.py   # main entrance.
        |-- README.md               # readme file.
    Usage:
        python patch_oversampling.py
    Notes:  # patches = 38,041
            # patches without verified IF stat   = 15,402 (41%)
            # patches with one verified IF stat  = 7,379  (19%)
            # patches with >=2 verified IF stats = 15,260 (40%)
            # verified IF stats = 135,378
            # possible patch variants = 1,083,024
            # restricted patch variants = 37,899
'''
