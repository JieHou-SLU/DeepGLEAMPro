# -*- coding: utf-8 -*-
"""protein_graph.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Sg9rSzj77o0db2GSgW6kABbC-4WBYRRy


!wget https://cs.slu.edu/~hou/downloads/QA_project/data/examples.zip --no-check-certificate

!wget https://cs.slu.edu/~hou/downloads/QA_project/data/examples_T0860.zip --no-check-certificate

!unzip  examples.zip

!unzip examples_T0860.zip

!pip install biopython

!pip install prody


"""

#!pip install biopython
from Bio import SeqIO, BiopythonWarning
import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore', BiopythonWarning)


import numpy as np
from Bio.PDB.PDBParser import PDBParser
from Bio.PDB.Polypeptide import three_to_one, one_to_three
import re
import pandas as pd


def load_fasta0(infile):
  fasta_sequence = list(SeqIO.parse(open(infile),'fasta'))[0]
  name, sequence = fasta_sequence.id, str(fasta_sequence.seq)
  return sequence

def load_pssm0(infile):
    with open(infile,'r') as pssm_file:
      file_lines = pssm_file.readlines()
      sequence = ''
      pssm_mat = []
      for line in file_lines:
        line = line.rstrip()
        line = re.sub(' +',' ',line)
        line = line.split(' ')
        if len(line) >= 44:
          sequence +=line[2]
          pssm_mat.append(list(map(float,line[3:3+20])))
      return sequence, pssm_mat

def load_fasta(infile):
  fasta_pd = pd.DataFrame(columns = ['ResId', 'AA'])
  fasta_sequence = list(SeqIO.parse(open(infile),'fasta'))[0]
  name, sequence = fasta_sequence.id, str(fasta_sequence.seq)
  fasta_pd['ResId'] = [str(i+1) for i in range(len(sequence))]
  fasta_pd['AA'] = [i for i in sequence]
  fasta_pd['ResId'] = fasta_pd['ResId'].astype(int)
  fasta_pd['AA'] = fasta_pd['AA'].str.upper() 
  return fasta_pd



def load_pssm(infile,sequence_pd):
    #infile = 'examples/T0860.pssm'
    seq = ''.join(sequence_pd['AA'].to_list())
    get_header = ''
    get_header_list= []
    header = False
    with open(infile,'r') as pssm_file:
        pssm_pd = pd.DataFrame(columns = ['ResId', 'AA']+['aa'+str(i) for i in range(20)]) 
        file_lines = pssm_file.readlines()
        for line in file_lines:
          line_orig = line.rstrip()
          line = line.rstrip()
          line = re.sub(' +',' ',line)
          line = line.split(' ')      
          if len(line) ==41 and header == False: # pssm may have 68 G   -1 -9 -7 -8 -9 -8 -7  8 -9-10-10 -8 -9-10 -9 -6 -8 -9-10-10 , so spacing is not best solution
            get_header = line_orig
            get_header_list = line
            header = True
            continue
          if len(line) >= 24:
            resid = int(line[1])
            resname = line[2]
            pssm_mat = {}
            pssm_mat['ResId'] = resid
            pssm_mat['AA'] = resname
            pssm_val = []
            if seq[resid-1] == resname:
                for i in range(0,20):
                    loc = get_header.find(get_header_list[i+1]) #['', '136', 'L', '-2', '-3', '-3'...]
                    if loc<0:
                        print("Error format in pssm!")
                        exit(-1)
                    val = line_orig[loc-2:loc+1]
                    val = re.sub(' +',' ',val)
                    #print('i: ',i)
                    #print('get_header: ',get_header)
                    #print('get_header_list: ',get_header_list)
                    #print('val: ',val)
                    #print('line_orig: ',line_orig)
                    pssm_mat['aa'+str(i)] =float(val)
            pssm_pd = pssm_pd.append(pssm_mat,  ignore_index = True) 
        #return pssm_pd
    pssm_pd['ResId'] = pssm_pd['ResId'].astype(int)
    pssm_pd['AA'] = pssm_pd['AA'].str.upper() 
    return pssm_pd

def load_ssa0(infile):
  fasta_sequence = list(SeqIO.parse(open(infile),'fasta'))[0]
  name, sequence = fasta_sequence.id, str(fasta_sequence.seq)
  return sequence

def load_ssa(infile):
  ssa_pd = pd.read_csv(infile, sep='\t')
  ssa_pd['#'] = ssa_pd['#'].astype(int)
  ssa_pd['AA'] = ssa_pd['AA'].str.upper() 
  return ssa_pd


def load_rr(infile):
  sequence_rr = pd.read_csv(infile, sep=' ', header=None, names=['Res1', 'Res2', 'Prob'])
  sequence_rr_sort = sequence_rr.sort_values(by = 'Prob', ascending=False) 
  sequence_rr_sort['Gap'] = abs(sequence_rr['Res1'] - sequence_rr['Res2'])
  sequence_rr_sort['Def'] = 'None'
  sequence_rr_sort.loc[(sequence_rr_sort['Gap']>=6) & (sequence_rr_sort['Gap']<=11),'Def']='short-range'
  sequence_rr_sort.loc[(sequence_rr_sort['Gap']>=12) & (sequence_rr_sort['Gap']<=23),'Def']='medium-range'
  sequence_rr_sort.loc[sequence_rr_sort['Gap']>=24,'Def']='long-range'
  sequence_rr['Res1'] = sequence_rr['Res1'].astype(int)
  sequence_rr['Res2'] = sequence_rr['Res2'].astype(int)
  return sequence_rr_sort


def load_lddt(infile):
  model_lddt = pd.read_csv(infile, sep='\s+', header=0, names=['ResId', 'Ca_dist', 'Ca_lddt'])
  model_lddt['ResId'] = model_lddt['ResId'].astype(int)
  return model_lddt

# per_res_env_score per_res_pair_score per_res_cbeta_score per_res_vdw_score per_res_rg_score per_res_cenpack_score per_res_co_score per_res_hs_score  per_res_ss_score per_res_rsigma_score per_res_sheet_score per_res_cen_hb_score

def load_rosetta(infile):
  model_energy = pd.read_csv(infile, sep='\s+', header=None, names=['ResId', 'per_res_env_score', 'per_res_pair_score','per_res_cbeta_score','per_res_vdw_score','per_res_rg_score','per_res_cenpack_score','per_res_co_score','per_res_hs_score','per_res_ss_score','per_res_rsigma_score','per_res_sheet_score','per_res_cen_hb_score'])
  model_energy['ResId'] = model_energy['ResId'].astype(int)
  return model_energy

def examine_ssa(ssa,seq_pd):
    # sometimes aa in dssp is missing
    seq_filter = seq_pd.loc[seq_pd['ResId'].isin(ssa['#'])]
    seq = ''.join(seq_filter['AA'].to_list())
    ss_seq = ''.join(ssa['AA'].to_list())
    if seq != ss_seq:  
        print("Inconsistency between ssa sequence!\n")  
        print(seq)
        print(ss_seq)
        return False
    else:
        #print('Match sequence in ssa')
        return True 

def examine_pdb(model_pdb,seq_pd):
    # sometimes aa in model is missing
    seq_filter = seq_pd.loc[seq_pd['ResId'].isin(model_pdb['ResId'])]
    seq = ''.join(seq_filter['AA'].to_list())
    pdb_seq = ''.join(model_pdb['AA'].to_list())
    if seq != pdb_seq:  
        print("Inconsistency between ssa sequence!\n")  
        print(seq)
        print(pdb_seq)
        return False
    else:
        #print('Match sequence in pdb')
        return True 

def examine_pssm(pssm,seq_pd):
    sequence = ''.join(seq_pd['AA'].to_list())
    pssm_seq = ''.join(pssm['AA'].to_list())
    if pssm_seq != sequence:
        print("Inconsistency between pssm sequence and original sequence!\n")
        print(pssm_seq)
        print(sequence)
        return False
    pssm_size = len(pssm['AA'].to_list())
    if pssm_size != len(sequence):
        print("Inconsistency between pssm matrix and number of residues in sequence!\n")
        return False
    #print('Match sequence in pssm')
    return True  

def examine_pssm0(pssm_seq,pssm_mat,sequence):
    if pssm_seq != sequence:
        print("Inconsistency between pssm sequence and original sequence!\n")
        print(pssm_seq)
        print(sequence)
        return False
    if len(pssm_mat) != len(sequence):
        print("Inconsistency between pssm matrix and number of residues in sequence!\n")
        return False
    #print('Match sequence in pssm')
    return True  

def load_pdb(infile):
    structure = PDBParser(QUIET=True).get_structure('test', infile)
    #model = structure.get_chains()
    model_coord = pd.DataFrame(columns = ['ResId', 'AA', 'x', 'y', 'z']) 
    for model in structure:
        for chain in model:
            for residue in chain:
                res_id = residue.get_id()[1]
                coord = residue['CA'].get_coord()
                try:
                    res_one = three_to_one(residue.get_resname())
                except:
                    res_one = 'X'
                #print(res_id,'->',res_one,'->',residue['CA'].get_coord())
                model_coord = model_coord.append({'ResId' : res_id, 'AA' : res_one, 'x' : coord[0], 'y' : coord[1], 'z' : coord[2]},  ignore_index = True) 
    model_coord['ResId'] = model_coord['ResId'].astype(int)
    model_coord['AA'] = model_coord['AA'].str.upper() 
    return model_coord

def generate_features(targetid,seqfile,ssfile,rrfile,pssmfile,prediction_dir,prediction_dssp, rosetta_dir, outfile, ss_win):
    import glob
    ss_win = ss_win
    target = targetid
    sequence_pd = load_fasta(seqfile)
    sequence_ss_pd = load_fasta(ssfile)
    sequence_rr = load_rr(rrfile)
    sequence_pssm = load_pssm(pssmfile,sequence_pd)
    #gdt_score = gdtfile
    #gdt_score_pd = pd.read_csv(gdt_score, sep='\t', header=None, names=['Model', 'GDT'])
    if not examine_pssm(sequence_pssm,sequence_pd):
        exit(-1)    
    model_list = []
    model_id = 0
    for filepath in glob.glob(prediction_dir+'/*'):
          model_id += 1
          filename = filepath.split('/')[-1]
          print("Processing ",model_id, ": ", filename)
          model_file = filepath
          model_ssa = load_ssa(prediction_dssp+'/'+filename+'.ssa')
          model_pdb = load_pdb(model_file)
          #model_lddt = load_lddt(lddt_dir+'/'+filename+'.error')
          filename2 = filename
          model_energy = load_rosetta(rosetta_dir+'/'+filename2+'.rosetta')
          
          
          # set gdt to 0 for inference
          model_gdt = 0
          
          if not examine_ssa(model_ssa,sequence_pd):
              exit(-1)

          if not examine_pdb(model_pdb,sequence_pd):
              exit(-1)
    
          model_pdb.insert(loc=0, column='target', value=target)
          model_pdb.insert(loc=1, column='model', value=filename)
          model_pdb.insert(loc=4, column='Ca_dist', value=0.0)
          model_pdb.insert(loc=5, column='Ca_lddt', value=0.0)
          model_pdb.insert(loc=6, column='GDT', value=0)
    
          model_pdb['pssm'] = ''
          model_pdb['ss'] = ''
    
          for idx in model_pdb.index:
              node_id = model_pdb['ResId'][idx]
              node_res = model_pdb['AA'][idx]
              node_x = model_pdb['x'][idx]
              node_y = model_pdb['y'][idx]
              node_z = model_pdb['z'][idx]
    
              ## load pssm
              node_pssm = list(sequence_pssm.loc[sequence_pssm['ResId']==node_id,:].values[0][2:])
              
              ## load rostta
              node_rosetta = list(model_energy.loc[model_energy['ResId']==node_id,:].values[0][1:])
    
              ## load lddt
              model_pdb.loc[idx,'Ca_dist'] = 0 # set lddt to 0 for inference
              model_pdb.loc[idx,'Ca_lddt'] = 0 # set lddt to 0 for inference
              
              ## load ss
              hwin = ss_win // 2
              node_ss = [0 for i in range(ss_win)]
              node_ss_idx = [i for i in range(node_id - hwin,node_id + hwin+1)]
              for i in range(ss_win): 
                  res_id = node_ss_idx[i]
                  if res_id >0 and res_id <= len(model_pdb['ResId']):
                      #print("check: ",model_ssa.loc[model_ssa['#'] == res_id,'Struct'].values)
                      model_ss_tmp = model_ssa.loc[model_ssa['#'] == res_id,'Struct'].values
                      if len(model_ss_tmp)==0: # dssp may miss amino acids
                          model_ss_at_id = 'X'
                      else:
                          model_ss_at_id = model_ss_tmp[0]
                
                      seq_ss_at_id = sequence_ss_pd.loc[sequence_ss_pd['ResId'] == res_id,'AA'].values[0]
                      #print(model_ss_at_id, seq_ss_at_id)
                      if model_ss_at_id == seq_ss_at_id:
                          node_ss[i] = 1
    
    
              model_pdb.loc[idx,'pssm'] = ','.join(map(str, node_pssm))
              model_pdb.loc[idx,'ss'] = ','.join(map(str, node_ss))
              model_pdb.loc[idx,'rosetta'] = ','.join(map(str, node_rosetta))
    
          ### load edge information using rr
          model_pdb['L5_short'] = -1
          model_pdb['L5_medium'] = -1
          model_pdb['L5_long'] = -1
          model_pdb['L2_short'] = -1
          model_pdb['L2_medium'] = -1
          model_pdb['L2_long'] = -1
          model_pdb['L_short'] = -1
          model_pdb['L_medium'] = -1
          model_pdb['L_long'] = -1
    
          short_rr = sequence_rr[sequence_rr['Def']=='short-range']
          short_rr = short_rr.sort_values(by = 'Prob', ascending=False) 
    
          medium_rr = sequence_rr[sequence_rr['Def']=='medium-range']
          medium_rr = medium_rr.sort_values(by = 'Prob', ascending=False) 
    
          long_rr = sequence_rr[sequence_rr['Def']=='long-range']
          long_rr = long_rr.sort_values(by = 'Prob', ascending=False) 
    
          L=len(sequence_pd)
          L5_long = long_rr.iloc[0:L//5]
          for i in L5_long.index:
            #print(i,'->',L5_long.loc[i,'Res1'])
            res1 = L5_long.loc[i,'Res1']
            res2 = L5_long.loc[i,'Res2']
            model_pdb.loc[model_pdb['ResId'] == res1,'L5_long'] = res2
            model_pdb.loc[model_pdb['ResId'] == res2,'L5_long'] = res1
    
          L5_short = short_rr.iloc[0:L//5]
          for i in L5_short.index:
            res1 = L5_short.loc[i,'Res1']
            res2 = L5_short.loc[i,'Res2']
            model_pdb.loc[model_pdb['ResId'] == res1,'L5_short'] = res2
            model_pdb.loc[model_pdb['ResId'] == res2,'L5_short'] = res1
    
          L5_medium = medium_rr.iloc[0:L//5]
          for i in L5_medium.index:
            res1 = L5_medium.loc[i,'Res1']
            res2 = L5_medium.loc[i,'Res2']
            model_pdb.loc[model_pdb['ResId'] == res1,'L5_medium'] = res2
            model_pdb.loc[model_pdb['ResId'] == res2,'L5_medium'] = res1
    
          L2_long = long_rr.iloc[0:L//2]
          for i in L5_long.index:
            #print(i,'->',L5_long.loc[i,'Res1'])
            res1 = L2_long.loc[i,'Res1']
            res2 = L2_long.loc[i,'Res2']
            model_pdb.loc[model_pdb['ResId'] == res1,'L2_long'] = res2
            model_pdb.loc[model_pdb['ResId'] == res2,'L2_long'] = res1
    
          L2_short = short_rr.iloc[0:L//2]
          for i in L2_short.index:
            res1 = L2_short.loc[i,'Res1']
            res2 = L2_short.loc[i,'Res2']
            model_pdb.loc[model_pdb['ResId'] == res1,'L2_short'] = res2
            model_pdb.loc[model_pdb['ResId'] == res2,'L2_short'] = res1
    
          L2_medium = medium_rr.iloc[0:L//2]
          for i in L2_medium.index:
            res1 = L2_medium.loc[i,'Res1']
            res2 = L2_medium.loc[i,'Res2']
            model_pdb.loc[model_pdb['ResId'] == res1,'L2_medium'] = res2
            model_pdb.loc[model_pdb['ResId'] == res2,'L2_medium'] = res1
    
          L_long = long_rr.iloc[0:L]
          for i in L5_long.index:
            #print(i,'->',L5_long.loc[i,'Res1'])
            res1 = L_long.loc[i,'Res1']
            res2 = L_long.loc[i,'Res2']
            model_pdb.loc[model_pdb['ResId'] == res1,'L_long'] = res2
            model_pdb.loc[model_pdb['ResId'] == res2,'L_long'] = res1
    
          L_short = short_rr.iloc[0:L]
          for i in L_short.index:
            res1 = L_short.loc[i,'Res1']
            res2 = L_short.loc[i,'Res2']
            model_pdb.loc[model_pdb['ResId'] == res1,'L_short'] = res2
            model_pdb.loc[model_pdb['ResId'] == res2,'L_short'] = res1
    
          L_medium = medium_rr.iloc[0:L]
          for i in L_medium.index:
            res1 = L_medium.loc[i,'Res1']
            res2 = L_medium.loc[i,'Res2']
            model_pdb.loc[model_pdb['ResId'] == res1,'L_medium'] = res2
            model_pdb.loc[model_pdb['ResId'] == res2,'L_medium'] = res1
    
    
          model_list.append(model_pdb)
          target_dataset = pd.concat(model_list, ignore_index=True)
          target_dataset.to_csv(outfile, sep = "\t", index=False)


import argparse


def get_args():
    parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter,
            epilog='EXAMPLE:\npython3 ')

    parser.add_argument('-t', type=str, required = True, dest = 'targetid', help="number of pdbs to use for each batch")
    parser.add_argument('-f', type=str, required = True, dest = 'seqfile', help="lengths of pdbs to use for each batch")
    parser.add_argument('-s', type=str, required = True, dest = 'ssfile', help="number of pdbs to use for training (use -1 for ALL)")
    parser.add_argument('-r', type=str, required = True, dest = 'rrfile', help="crop size (window) for training, 64, 128, etc. ")
    parser.add_argument('-p', type=str, required = True, dest = 'pssmfile', help="# of epochs")
    parser.add_argument('-d', type=str, required = True, dest = 'prediction_dir', help="residual arch depth")
    parser.add_argument('-k', type=str, required = True, dest = 'prediction_dssp', help="number of convolutional filters in each layer")
    parser.add_argument('-e', type=str, required = True, dest = 'rosetta_dir', help="rosetta path")
    parser.add_argument('-o', type=str, required = True, dest = 'outfile', help="1 = Evaluate only, don't train")
    parser.add_argument('-w', type=int, required = True, dest = 'ss_win', help="1 = Train/Evaluate on noncanonical pairs")

    
    args = parser.parse_args()
    return args
    


args = get_args()

targetid                = args.targetid 
seqfile                  = args.seqfile 
ssfile           = args.ssfile   
rrfile           = args.rrfile   
pssmfile                = args.pssmfile 
prediction_dir                 = args.prediction_dir 
prediction_dssp               = args.prediction_dssp 
rosetta_dir                   = args.rosetta_dir 
outfile            = args.outfile
ss_win            = args.ss_win


generate_features(targetid,seqfile,ssfile,rrfile,pssmfile,prediction_dir,prediction_dssp,rosetta_dir, outfile, ss_win=ss_win)


    