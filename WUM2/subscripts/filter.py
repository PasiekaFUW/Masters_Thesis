#Selection by W. Matyszkiewicz
def apply_selection(df):
    selection = (
        (df['pt_1'] > 20)
        & (df['pt_2'] > 20)
        & (abs(df['eta_1']) < 2.4)
        & (abs(df['eta_2']) < 2.4)
        & (df["idDeepTau2018v2p5VSjet_2"] >= 5)
        & (df["idDeepTau2018v2p5VSe_2"] >= 2)
        & (df["idDeepTau2018v2p5VSmu_2"] >= 4)
    )
    return df[selection].copy()