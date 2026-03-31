import uproot
import pandas as pd
import awkward as ak
import time
import re
start_time = time.time()

#neutral_particles = [-12, 12, -14, 14, -16, 16, -2112, 2112, -111, 111, -3122, 3122, -3212, 3212,
#                        -421, 421, -311, 311, -130, 130, 2000000101, 1000180400, 130, 310, 3322, -3322,# 221, 331, 443]

# cząstki neutralne, które uznajemy, że są niewidoczne w detektorze: neutrina i neutrony
# neutrony w zasadzie można rejestrować, ale niska efektywność - obejrzeć pracę MicroBooNE

neutral_particles = [-12, 12, -14, 14, -16, 16, 2112]

# Dla każdej kolumny w dataframe próba dopasowania wzorca (\D+)_(\d+)
# (\D+) - (prefix) jeden lub więcej znaków nienumerycznych
# _ - znak podkreslenia
# (\d+) - (num) liczba
# Np. dla P_3 prefix = "P", num="3"

def sort_columns_by_suffix(df):
    def sort_key(col):
        match = re.match(r"(\D+)_(\d+)", col)
        
        if match:
            prefix, num = match.groups()
            if (prefix[0]=='P'):
                return int(num), 'A'
            elif(prefix[0]=='E'):
                return int(num), 'z'
            return int(num), prefix
        else:
            
            return float(0), col  
    
    return df[sorted(df.columns, key=sort_key)]
# df.columns zwraca Index z nazwami kolumn
# sorted bierze każdą kolumnę i wywołuje sort_key
# sorted - porównuje krotki i ustawia je w dobrej kolejności

# Funkcja do wybierania niektórych pól z napisu EvtCode (tutaj tych, które
# są po nu: i proc:
def extract_field(text, field):
    match = re.search(rf"{field}:([^;]+)", text)
    return match.group(1) if match else None


def extract_data(filename, exportname):
    
    file = uproot.open(filename)
    tree = file["gRooTracker"]
    

    stdhep_status=tree["StdHepStatus"].array()
    stdhep_status_df=ak.to_dataframe(stdhep_status)
    del stdhep_status

    stdhep_status_df =stdhep_status_df.reset_index()

    stdhep_status_df.rename(columns={"values": "Status"}, inplace=True)

    # Children
                     
    stdhep_fchild=tree["StdHepFd"].array()
    stdhep_fchild_df=ak.to_dataframe(stdhep_fchild)
    del stdhep_fchild

    stdhep_fchild_df =stdhep_fchild_df.reset_index()

    stdhep_fchild_df.rename(columns={"values": "Fchild"}, inplace=True)

    #
    
    stdhep_lchild=tree["StdHepLd"].array()
    stdhep_lchild_df=ak.to_dataframe(stdhep_lchild)
    del stdhep_lchild
    
    stdhep_lchild_df =stdhep_lchild_df.reset_index()


    stdhep_lchild_df.rename(columns={"values": "Lchild"}, inplace=True)

    #
    
    stdhep_Pdg=tree["StdHepPdg"].array()
    stdhep_Pdg_df=ak.to_dataframe(stdhep_Pdg)
    del stdhep_Pdg

    stdhep_Pdg_df =stdhep_Pdg_df.reset_index()
    
    stdhep_Pdg_df.rename(columns={"values": "Pdg"}, inplace=True)

    #Pojedyncze nawiasy df["Pdg"] → zwraca Series (1D, bez nagłówka kolumn jako tabeli).
    #Podwójne nawiasy df[["Pdg"]] → zwraca DataFrame (2D, zachowuje nagłówki i "tabelową" strukturę).
    #.join działa między DataFrameami
    
    stdhep_Pdg_Status_df=stdhep_Pdg_df[["Pdg"]].join(stdhep_status_df[["Status"]])

    stdhep_Pdg_Status_Fc_df=stdhep_Pdg_Status_df.join(stdhep_fchild_df[["Fchild"]])
    stdhep_Pdg_Status_Fc_Lc_df=stdhep_Pdg_Status_Fc_df.join(stdhep_lchild_df[["Lchild"]])     
    
    del stdhep_Pdg_df
    del stdhep_status_df
    del stdhep_Pdg_Status_df
    del stdhep_Pdg_Status_Fc_df
    
    stdhep_p4 = tree["StdHepP4"].array()
    
    stdhep_p4_rec = ak.zip({
        
        "px": stdhep_p4[..., 0],
        "py": stdhep_p4[..., 1],
        "pz": stdhep_p4[..., 2],
        "E":  stdhep_p4[..., 3],
    })


    del stdhep_p4
    stdhep_df = ak.to_dataframe(stdhep_p4_rec)
    del stdhep_p4_rec

    stdhep_df = stdhep_df.reset_index()

    stdhep_df.rename(columns={"entry": "EvtNum", "subentry": "particle"}, inplace=True)
    
    # EvtNum column

    df = tree.arrays("EvtNum", library="pd")


    #proc_split=ak.to_dataframe(tree['EvtCode/fString'].array())['values']

    # EvtCode/fString column
    
    proc_split=ak.to_dataframe(tree['EvtCode/fString'].array())  


    proc_split=proc_split.reset_index() 
    proc_split.rename(columns={"entry": "EvtNum","values": "EvtCode"}, inplace=True)

    # Choose what is behind nu: and proc:
    nu_df = proc_split['EvtCode'].apply(lambda x: extract_field(x, "nu"))
    proc_df = proc_split['EvtCode'].apply(lambda x: extract_field(x, "proc"))

    
    # Choose interaction type
    # Everything between Weak[ ... and ]
    general_df = proc_df.str.extract(r"Weak\[(.*?)\]")

    general_df.rename(columns={0: "CCNC"}, inplace=True)
    
    # Everything after ] up to ;, without , at the beginning

    inttype_df = proc_df.str.extract(r"\](.*?)(?:;|$)").iloc[:, 0].str.lstrip(",")  

    nu_df=nu_df.to_frame(name="Nu")
    #general_df is already a data frame
    #general_df.name="CCNC"
    inttype_df=inttype_df.to_frame(name="IntType")

    all_df = pd.concat([nu_df,general_df,inttype_df],axis=1)

    
    # Do not want subentry column with numbers of particles in an event
    # some of particles will be reset anyway

    # Axis = 1 -> removing columns
    stdhep_df=stdhep_df.drop('particle',axis=1)

    # To ważne ! Łączenie po kolumnie

    # Join  EvtNum column and EvtCode column on the basis of EvtNum
    
    # merged = pd.merge(df,proc_split, on="EvtNum")
    merged_from_EvtCode = pd.concat([df,all_df],axis=1)
    
    #del proc_split
    del df

    # Joining  EvtNum+EvtCode column and StdHepP4 column on the basis of EvtNum    
    
    merged_P4 = pd.merge(merged_from_EvtCode,stdhep_df, on="EvtNum")

    del stdhep_df

    # Dlaczego to było?
    #proc_split

    # Add column with status codes
        
    total_merged=merged_P4.join(stdhep_Pdg_Status_Fc_Lc_df)    
    #del merged

    # Removing non-final particles
    
    total_merged=total_merged[total_merged["Status"] == 1]
    
    # Czy nie trzeba zresetować indeksu? Indeksy są nie po kolei, bo część cząstek jest usuniętych

    # Remove rows with particles  in the list neutral_particles
    
    total_merged=total_merged[~total_merged["Pdg"].isin(neutral_particles)]

    # Remove Status column and EvtCode column

    # Axis = 1 -> removing columns    
    #total_merged=total_merged.drop(['Status','EvtCode'],axis=1)
    # usuwane, bo pivot dobrze nie zadziała - potem trzeba dodać
    total_merged=total_merged.drop(['Status','CCNC','IntType','Nu'],axis=1)


    # Groups partcles belonging to the same event
    # Create numbers for all particles in the group, starting from 1 (+1)
    # (In case the particles order was incorrect)
    # Create row_number column (last one)
    
    total_merged['row_number'] = total_merged.groupby('EvtNum').cumcount() + 1

    # Reshape the data frame   
    
    #Pivot the table to create separate columns
    # pivot - przestawienie danych z formatu "long" na "wide" 
    # – każda unikalna wartość w kolumnie EvtNum staje się wierszem w nowej tabeli.
    # - każda unikalna wartość w kolumnie row_number staje się nową kolumną w wyniku
    # kolumny z wielopoziomowymi nazwami (MultiIndex), pierwszy poziom to nazwa oryginalnej kolumny,
    # a drugi to row_number
    # Pozostałe kolumny będą rozłożone w siatce EvtNum x row_number
    
    df_wide = total_merged.pivot(index='EvtNum', columns='row_number')

    # Flattening  
    
    #Flatten MultiIndex columns
    df_wide.columns = [f'{col}_{num}' for col, num in df_wide.columns]
    
    #Reset index
    df_wide = df_wide.reset_index()

    # Wyrzuci EvtCode i EvtNum na początek, gdyby nie było na początku
    # Ustawia Pdg_1 px_1 py_1 pz_1 E_1  i dalej dla kolejnych cząstek tak samo
    # Gdyby tego nie było to mielibyśmy
    # px_1 px_2 px_3 px_4 ... i dalej py_1 itd
    df_wide=sort_columns_by_suffix(df_wide)

    # Join columns from EvtCode

    df_total = pd.merge(merged_from_EvtCode,df_wide, on="EvtNum")
    del merged_from_EvtCode,df_wide

    
    # Replace NaN by 0
    
    df_total.fillna(0, inplace=True)
    #df_wide.fillna(0, inplace=True)

    # Save to csv file
    
    df_total.to_csv(exportname, index=False)
    

# All events, 3_04_02   
#extract_data('gntp.0.ghep_numu_1.gtrac.root','gntp.0.ghep_numu_1_3_04_02.gtrac_1.csv')
#extract_data('gntp.0.ghep_nutau_1.gtrac.root','gntp.0.ghep_nutau_1_3_04_02.gtrac_1.csv')

# CCQE
# 3_4_02
# extract_data('gntp.0.ghep_nutau_CCQE_3_06_02.gtrac.root','gntp.0.ghep_nutau_CCQE_3_06_02.gtrac.csv')
# extract_data('gntp.0.ghep_numu_CCQE_3_06_02.gtrac.root','gntp.0.ghep_numu_CCQE_3_06_02.gtrac.csv')
# extract_data('gntp.0.ghep_nutau_CCQE_3_04_02.gtrac.root','gntp.0.ghep_nutau_CCQE_3_04_02.gtrac.csv')
# extract_data('gntp.0.ghep_numu_CCQE_3_04_02.gtrac.root','gntp.0.ghep_numu_CCQE_3_04_02.gtrac.csv')


#print("--- %s seconds ---" % (time.time() - start_time))


def clean_pd(df):
    #clean nulls
    print(f"Number of events before cleaning: {len(df)}")
    df = df.dropna(subset=['EvtNum', 'CCNC', 'IntType'])
    df.info()
    df.head()
    print(f"Number of events after cleaning: {len(df)}")
    return df
    
