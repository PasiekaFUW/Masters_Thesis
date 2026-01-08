# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: step1 --conditions 123X_mcRun4_realistic_v3 -n 2 --era Phase2C9 --eventcontent FEVTDEBUGHLT --runUnscheduled file:/eos/cms/store/relval/CMSSW_11_0_0/RelValTTbar_14TeV/GEN-SIM-DIGI-RAW/PU25ns_110X_mcRun4_realistic_v3_2026D49PU200-v2/10000/01054EE2-1B51-C449-91A2-5202A60D16A3.root -s RAW2DIGI,L1TrackTrigger,L1 --datatier FEVTDEBUGHLT --customise SLHCUpgradeSimulations/Configuration/aging.customise_aging_1000,L1Trigger/Configuration/customisePhase2TTNoMC.customisePhase2TTNoMC,Configuration/DataProcessing/Utils.addMonitoring,L1Trigger/Configuration/customisePhase2FEVTDEBUGHLT.customisePhase2FEVTDEBUGHLT --geometry Extended2026D49 --fileout file:/tmp/step1_Reprocess_TrackTrigger_L1.root --no_exec --nThreads 8 --python step1_L1_ProdLike.py --processName=L1REPR
import FWCore.ParameterSet.Config as cms

from Configuration.Eras.Era_Phase2C17I13M9_cff import Phase2C17I13M9

process = cms.Process('L1REPROCESS',Phase2C17I13M9)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.Geometry.GeometryExtendedRun4DefaultReco_cff') # Run4 or 2026
process.load("TrackingTools.RecoGeometry.RecoGeometries_cff")
process.load("TrackingTools.TrackRefitter.TracksToTrajectories_cff")
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.RawToDigi_cff')
process.load('Configuration.StandardSequences.L1TrackTrigger_cff')
process.load('Configuration.StandardSequences.SimL1Emulator_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load("TrackingTools.RecoGeometry.RecoGeometries_cff")

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(10000), #10 000
    output = cms.optional.untracked.allowed(cms.int32,cms.PSet)
)

# Input source
prefixPath = '/scratch_cmsse/akalinow/CMS/Data/SingleMu/14_2_1_21_03_2025/'
#prefixPath = '/home/akalinow/scratch/CMS/OMTF/Production/PrivateMCProduction/'

process.source = cms.Source("PoolSource",
                            fileNames = cms.untracked.vstring('file:'+prefixPath+'SingleMu_OneOverPt_1_100_m_1.root'),
                            secondaryFileNames = cms.untracked.vstring(),
                                      dropDescendantsOfDroppedBranches=cms.untracked.bool(False),
          inputCommands=cms.untracked.vstring('keep *',
                                              'drop *_l1tKMTFMuonsGmt_*_*'),
          eventsToProcess = cms.untracked.VEventRange(
            '1:1:4',
            '1:2:139',
            '1:2:169'
          )  
)

import glob
import numpy as np
fileList = glob.glob(prefixPath+'/*.root')
if not len(fileList):
    fileList = glob.glob(prefixPath+'/*/*/*/*/*.root')
#fileList = np.random.default_rng().permutation(fileList)
fileList = ['file:'+aFile for aFile in fileList]

process.source.fileNames = cms.untracked.vstring(fileList)
#print("Input files: ", process.source.fileNames) #GJ temporarily commented
#'''


process.MessageLogger.files.muCorrelatorEventPrint = dict()
process.MessageLogger.cerr.noTimeStamps = cms.untracked.bool(True)
process.MessageLogger.cerr.threshold = "DEBUG"
process.MessageLogger.cerr.DEBUG = dict(limit = -1)
process.MessageLogger.cerr.OMTFReconstruction = dict(limit = -1)
process.MessageLogger.cerr.gmtDataDumper = dict(limit = -1)
process.MessageLogger.cerr.l1tGMTMuons = dict(limit = -1)
process.MessageLogger.cerr.trackMatching = dict(limit = -1)
process.MessageLogger.cerr.TrackerMuon = dict(limit = -1)
process.MessageLogger.cerr.ConvertedTTTrack = dict(limit = -1)
process.MessageLogger.cerr.SAMuonsWithCommonStubInfo = dict(limit = -1)
process.MessageLogger.debugModules = ['simOmtfPhase2Digis', 'l1tGMTMuons', 'l1tGMTStubs', 'gmtDataDumper', 'SAMuonsWithCommonStubInfo']
process.MessageLogger.debugModules = []


# process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32(1000)
process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))



# Geometry
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:phase2_realistic_T33', '')

####Event Setup Producer (Run4 GlobalTag has outdated OMTF parameters)
process.load('L1Trigger.L1TMuonOverlapPhase1.fakeOmtfParams_cff')
process.omtfParams.configXMLFile = cms.FileInPath("L1Trigger/L1TMuon/data/omtf_config/hwToLogicLayer_0x0209.xml")
process.omtfParams.patternsXMLFiles = cms.VPSet(
        cms.PSet(patternsXMLFile = cms.FileInPath("L1Trigger/L1TMuon/data/omtf_config/Patterns_ExtraplMB1nadMB2DTQualAndRFixedP_DT_2_2_t30__classProb17_recalib2.xml")),
)
#reading config and patterns from the DB2_2
process.esProd = cms.EDAnalyzer("EventSetupRecordDataGetter",
   toGet = cms.VPSet(
      cms.PSet(record = cms.string('L1TMuonOverlapParamsRcd'),
               data = cms.vstring('L1TMuonOverlapParams'))
                   ),
   verbose = cms.untracked.bool(False)
)
############################################
# Output ROOT file service
process.TFileService = cms.Service("TFileService", 
                                    fileName = cms.string('data_dump.root'), 
                                    closeFileFast = cms.untracked.bool(True) )
############################################
##
#Calibrate Digi
process.load("L1Trigger.DTTriggerPhase2.CalibratedDigis_cfi")
process.CalibratedDigis.dtDigiTag = "simMuonDTDigis" 
process.CalibratedDigis.scenario = 0
############################################
#DTTriggerPhase2
process.load("L1Trigger.DTTriggerPhase2.dtTriggerPhase2PrimitiveDigis_cfi")
process.dtTriggerPhase2PrimitiveDigis.debug = False
process.dtTriggerPhase2PrimitiveDigis.dump = False
process.dtTriggerPhase2PrimitiveDigis.scenario = 0
process.DTPhase2DigisPath = cms.Path(process.CalibratedDigis*process.dtTriggerPhase2PrimitiveDigis)
############################################
## CSCTriggerPhase2
from L1Trigger.L1TMuonEndCapPhase2.simCscTriggerPrimitiveDigisForEMTF_cfi import *
from L1Trigger.L1TMuonEndCapPhase2.rpcRecHitsForEMTF_cfi import *
from L1Trigger.L1TMuonEndCapPhase2.simEmtfDigisPhase2_cfi import *
process.CSCPhase2DigisPath = cms.Path(simCscTriggerPrimitiveDigisForEMTF*rpcRecHitsForEMTF*simEmtfDigisPhase2)
############################################

process.load("TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorAlong_cfi")
############################################
#Phase2 GMT
process.load("L1Trigger.Phase2L1GMT.gmt_cff")
process.gmtTkMuons.isolation.IsodumpForHLS = 0
process.gmtTkMuons.trackingParticleInputTag = cms.InputTag("mix", "MergedTrackTruth")
process.gmtTkMuons.mcTruthTrackInputTag = cms.InputTag("TTTrackAssociatorFromPixelDigisExtended", "Level1TTTracks")
process.gmtTkMuons.srcTracks = cms.InputTag("l1tTTTracksFromExtendedTrackletEmulation","Level1TTTracks")
process.gmtTkMuons.dumpToRoot = cms.bool(True)
#process.GMTPhase2Path = cms.Path(process.L1TrackTrigger*process.phase2GMT*process.SAMuonsWithCommonStubInfo)
process.GMTPhase2Path = cms.Path(process.phase2GMT*process.SAMuonsWithCommonStubInfo)
############################################
####OMTF Emulator
import L1Trigger.L1TMuonOverlapPhase2.simOmtfPhase2Digis_cfi
process.simOmtfPhase2Digis=L1Trigger.L1TMuonOverlapPhase2.simOmtfPhase2Digis_cfi.simOmtfPhase2Digis.clone() 
process.simOmtfPhase2Digis.dumpHitsToROOT = cms.bool(True)
process.simOmtfPhase2Digis.dumpResultToXML = cms.bool(False)
process.simOmtfPhase2Digis.candidateSimMuonMatcher = cms.bool(True)
process.simOmtfPhase2Digis.candidateSimMuonMatcherType = cms.string("propagation")   
process.simOmtfPhase2Digis.simTracksTag = cms.InputTag('g4SimHits')
process.simOmtfPhase2Digis.simVertexesTag = cms.InputTag('g4SimHits')
process.simOmtfPhase2Digis.muonMatcherFile = cms.FileInPath("L1Trigger/L1TMuon/data/omtf_config/muonMatcherHists_100files_smoothStdDev_withOvf.root")

process.simOmtfPhase2DigisLUT=process.simOmtfPhase2Digis.clone() 
process.simOmtfPhase2DigisLUT.neuralNetworkFile = cms.FileInPath("L1Trigger/L1TMuon/data/omtf_config/lutNN_omtfRegression_v430_FP.xml")
process.simOmtfPhase2DigisLUT.minDtPhiQuality = cms.int32(0)
process.simOmtfPhase2DigisLUT.minDtPhiBQuality = cms.int32(2)

prefix = "/home/akalinow/scratch/CMS/OMTF/PhaseII/omtf_nn_py/omtf_nn/training/"
model_tag = '2025_Feb_27_16_05_19_classic_512_256_128_1'
process.simOmtfPhase2DigisNN=process.simOmtfPhase2Digis.clone() 
process.simOmtfPhase2DigisNN.tf_neuralNetworkFile = cms.string(prefix + model_tag)
# process.omtfPath = cms.Path(process.esProd*process.simOmtfPhase2Digis*process.simOmtfPhase2DigisNN)
process.omtfPath = cms.Path(process.esProd*process.simOmtfPhase2Digis)

############################################
####OMTF Analyzer
process.load('omtfTree_cfi')
#############################################
# Path and EndPath definitions
process.endjob_step = cms.EndPath(process.endOfProcess)

###Gen level filter configuration
process.SimTrackFilter = cms.EDFilter("SimTrackFilter",
                                minNumber = cms.uint32(1),
                                src = cms.InputTag("g4SimHits"),
                                cut = cms.string("abs(type)==13 && abs(momentum.pt)>10 && abs(momentum.eta)<1") 
                                # cut = cms.string("abs(type)==13")
                                )
process.GenMuFilterPath = cms.Path(process.SimTrackFilter)
process.muAnalyzerPath = cms.Path(process.SimTrackFilter*process.omtfTree)

# Schedule definition
process.schedule = cms.Schedule(process.GenMuFilterPath,process.DTPhase2DigisPath,process.omtfPath,process.GMTPhase2Path,process.muAnalyzerPath,process.endjob_step)

#Setup FWK for multithreaded
process.options.numberOfThreads = 1
process.options.numberOfStreams = 0
process.options.numberOfConcurrentLuminosityBlocks = 1
process.options.eventSetup.numberOfConcurrentIOVs = 1

# customisation of the process.

# Automatic addition of the customisation function from SLHCUpgradeSimulations.Configuration.aging
from SLHCUpgradeSimulations.Configuration.aging import customise_aging_1000 

#call to customisation function customise_aging_1000 imported from SLHCUpgradeSimulations.Configuration.aging
process = customise_aging_1000(process)

# Automatic addition of the customisation function from L1Trigger.Configuration.customisePhase2TTOn110
from L1Trigger.Configuration.customisePhase2TTOn110 import customisePhase2TTOn110 

#call to customisation function customisePhase2TTNoMC imported from L1Trigger.Configuration.customisePhase2TTNoMC
process = customisePhase2TTOn110(process)

# Automatic addition of the customisation function from L1Trigger.Configuration.customisePhase2TTNoMC
from L1Trigger.Configuration.customisePhase2TTNoMC import customisePhase2TTNoMC 

#call to customisation function customisePhase2TTNoMC imported from L1Trigger.Configuration.customisePhase2TTNoMC
process = customisePhase2TTNoMC(process)

# Automatic addition of the customisation function from Configuration.DataProcessing.Utils
from Configuration.DataProcessing.Utils import addMonitoring 

#call to customisation function addMonitoring imported from Configuration.DataProcessing.Utils
process = addMonitoring(process)
# End of customisation functions

# Customisation from command line

# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion
