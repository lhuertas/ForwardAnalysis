import FWCore.ParameterSet.Config as cms

##---------------------------------------

from L1TriggerConfig.L1GtConfigProducers.L1GtTriggerMaskAlgoTrigConfig_cff import *
from L1TriggerConfig.L1GtConfigProducers.L1GtTriggerMaskTechTrigConfig_cff import *
es_prefer_l1GtTriggerMaskAlgoTrig = cms.ESPrefer("L1GtTriggerMaskAlgoTrigTrivialProducer","l1GtTriggerMaskAlgoTrig")
es_prefer_l1GtTriggerMaskTechTrig = cms.ESPrefer("L1GtTriggerMaskTechTrigTrivialProducer","l1GtTriggerMaskTechTrig")

##---------------------------------------

###--------
from ForwardAnalysis.AnalysisSequences.primaryVertexFilter_cfi import *
##---------------------
from ForwardAnalysis.AnalysisSequences.filterScraping_cfi import *
##-------------
from CommonTools.RecoAlgos.HBHENoiseFilter_cfi import *
##-------------

from ForwardAnalysis.AnalysisSequences.hltFilter_cfi import *
hltBscMinBiasORBptxPlusORMinusFilter = hltFilter.clone(HLTPaths = ['HLT_L1_BscMinBiasOR_BptxPlusORMinus'])

from ForwardAnalysis.Utilities.analysisTracks_cfi import *

from ForwardAnalysis.Utilities.selectTracksAssociatedToPV_cfi import *
selectTracksAssociatedToPV.src = "analysisTracks"
selectTracksAssociatedToPV.vertexTag = "offlinePrimaryVertices"
selectTracksAssociatedToPV.maxDistanceFromVertex = 0.4

#------------------------------
# Particle flow

# Add EtaMax
from ForwardAnalysis.Utilities.pfCandidateSelector_cfi import pfCandidateSelector as pfCandidateNoiseThresholds
from ForwardAnalysis.Utilities.ExcludeHFEdgesStringCut import ExcludeHFEdgesStringCut
from ForwardAnalysis.Utilities.PFCandidateNoiseStringCut import PFCandidateNoiseStringCut
# Change thresholds here if needed
#from ForwardAnalysis.Utilities.pfThresholds_cfi import pfThresholds
from ForwardAnalysis.ForwardTTreeAnalysis.pfThresholds_cfi import pfThresholds
pfStrCut1 = ExcludeHFEdgesStringCut().cut()
pfStrCut2 = PFCandidateNoiseStringCut(pfThresholds).cut()
pfStrCut = '%s & %s' % (pfStrCut1,pfStrCut2)
pfCandidateNoiseThresholds.cut = pfStrCut
# Change to no pile-up collection
#pfCandidateNoiseThresholds.src = "pfNoPileUpPFlow" 

from ForwardAnalysis.Utilities.etaMaxCandViewSelector_cfi import etaMaxCandViewSelector as etaMaxPFCands
from ForwardAnalysis.Utilities.etaMinCandViewSelector_cfi import etaMinCandViewSelector as etaMinPFCands
etaMaxPFCands.src = "pfCandidateNoiseThresholds"
etaMinPFCands.src = "pfCandidateNoiseThresholds"

from ForwardAnalysis.AnalysisSequences.genChargedParticles_cfi import genChargedParticles
from ForwardAnalysis.AnalysisSequences.genStableParticles_cfi import genStableParticles
genStableParticles.cut = 'status = 1 & ( ( pdgId != 2212 ) | ( pdgId == 2212 & abs(pz) < %f ) )' % (0.75*3500.0)
genProtonDissociative = genStableParticles.clone( cut = 'pdgId == 9902210' )
etaMaxGen = etaMaxPFCands.clone(src = "genStableParticles")
etaMinGen = etaMinPFCands.clone(src = "genStableParticles")

from ForwardAnalysis.AnalysisSequences.edmNtupleCandView_cfi import edmNtupleCandView
edmNtupleEtaMax = edmNtupleCandView.clone(src = "etaMaxPFCands")
edmNtupleEtaMax.variables = cms.VPSet( cms.PSet( tag = cms.untracked.string("etaMax"),
                                                 quantity = cms.untracked.string("eta") ) )
edmNtupleEtaMin = edmNtupleCandView.clone(src = "etaMinPFCands")
edmNtupleEtaMin.variables = cms.VPSet( cms.PSet( tag = cms.untracked.string("etaMin"),
                                                 quantity = cms.untracked.string("eta") ) )

edmNtupleMxGen = edmNtupleCandView.clone(src = "genProtonDissociative")
edmNtupleMxGen.variables = cms.VPSet( cms.PSet( tag = cms.untracked.string("Mx"),
                                                quantity = cms.untracked.string("mass") ) )
edmNtupleEtaMaxGen = edmNtupleEtaMax.clone(src = "etaMaxGen")
edmNtupleEtaMinGen = edmNtupleEtaMin.clone(src = "etaMinGen")

from ForwardAnalysis.AnalysisSequences.etaMaxSelector_cfi import etaMaxSelector as etaMaxFilter
etaMaxFilter.src = "etaMaxPFCands"
from ForwardAnalysis.AnalysisSequences.etaMinSelector_cfi import etaMinSelector as etaMinFilter
etaMinFilter.src = "etaMinPFCands"

etaMaxGenFilter = etaMaxFilter.clone(src = "etaMaxGen")
etaMinGenFilter = etaMinFilter.clone(src = "etaMinGen")
#------------------------------

from ForwardAnalysis.Utilities.caloActivityFilter_cfi import caloActivityFilter
caloVetoHFPlus = caloActivityFilter.clone(NTowersMaxHFPlus=0)
caloVetoHFMinus = caloActivityFilter.clone(NTowersMaxHFMinus=0)
caloActivityFilter.EnergyThresholdHB = 1.5
caloActivityFilter.EnergyThresholdHE = 2.0
caloActivityFilter.EnergyThresholdHF = 4.0
'''
from ForwardAnalysis.Utilities.castorActivityFilter_cfi import castorActivityFilter
castorActivityFilter.CastorRecHitTag = "castorRecHitCorrector"
castorActivityFilter.SumEMaxCastor = 250.

castorInvalidDataFilter = cms.EDFilter("CastorInvalidDataFilter")
castorVeto = cms.Sequence(castorInvalidDataFilter + castorActivityFilter)
castorTag = cms.Sequence(castorInvalidDataFilter + ~castorActivityFilter)
'''
##-----------------------------------------------------------------
from ForwardAnalysis.Utilities.hcalActivitySummary_cfi import *
hcalActivitySummary.DiscardFlaggedTowers = False
hcalActivitySummaryScale090 = hcalActivitySummary.clone(ApplyEnergyScale = True,EnergyScaleFactorHB = 0.90,EnergyScaleFactorHE = 0.90,EnergyScaleFactorHF = 0.90)
hcalActivitySummaryScale092 = hcalActivitySummary.clone(ApplyEnergyScale = True,EnergyScaleFactorHB = 0.92,EnergyScaleFactorHE = 0.92,EnergyScaleFactorHF = 0.92)
hcalActivitySummaryScale095 = hcalActivitySummary.clone(ApplyEnergyScale = True,EnergyScaleFactorHB = 0.95,EnergyScaleFactorHE = 0.95,EnergyScaleFactorHF = 0.95)
hcalActivitySummaryScale098 = hcalActivitySummary.clone(ApplyEnergyScale = True,EnergyScaleFactorHB = 0.98,EnergyScaleFactorHE = 0.98,EnergyScaleFactorHF = 0.98)
hcalActivitySummaryScale102 = hcalActivitySummary.clone(ApplyEnergyScale = True,EnergyScaleFactorHB = 1.02,EnergyScaleFactorHE = 1.02,EnergyScaleFactorHF = 1.02)
hcalActivitySummaryScale105 = hcalActivitySummary.clone(ApplyEnergyScale = True,EnergyScaleFactorHB = 1.05,EnergyScaleFactorHE = 1.05,EnergyScaleFactorHF = 1.05)
hcalActivitySummaryScale108 = hcalActivitySummary.clone(ApplyEnergyScale = True,EnergyScaleFactorHB = 1.08,EnergyScaleFactorHE = 1.08,EnergyScaleFactorHF = 1.08)
hcalActivitySummaryScale110 = hcalActivitySummary.clone(ApplyEnergyScale = True,EnergyScaleFactorHB = 1.10,EnergyScaleFactorHE = 1.10,EnergyScaleFactorHF = 1.10)
"""
from Utilities.AnalysisTools.hcalActivityFilter_cfi import hcalActivityFilter
hcalActivityFilter.EnergyThresholdHB = 1.5
hcalActivityFilter.EnergyThresholdHE = 2.0
hcalActivityFilter.EnergyThresholdHF = 4.0hcalVetoHBPlusAndMinus = hcalActivityFilter.clone(NTowersMaxHBPlus = 0, NTowersMaxHBMinus = 0)
hcalVetoHBHEPlusAndMinus = hcalActivityFilter.clone(NTowersMaxHBPlus = 0, NTowersMaxHEPlus = 0, NTowersMaxHBMinus
 = 0, NTowersMaxHEMinus = 0)
hcalVetoSumEMaxHBPlusAndMinus4 = hcalActivityFilter.clone(SumEMaxHBPlus = 4.0, SumEMaxHBMinus = 4.0)
hcalVetoSumEMaxHBPlusAndMinus8 = hcalActivityFilter.clone(SumEMaxHBPlus = 8.0, SumEMaxHBMinus = 8.0)
hcalVetoSumEMaxHBPlusAndMinus12 = hcalActivityFilter.clone(SumEMaxHBPlus = 12.0, SumEMaxHBMinus = 12.0)
hcalVetoSumEMaxHBPlusAndMinus16 = hcalActivityFilter.clone(SumEMaxHBPlus = 16.0, SumEMaxHBMinus = 16.0)
"""

##-----------------------------------------------------------------
# Event selection
offlineSelection = cms.Sequence(primaryVertexFilter + filterScraping + HBHENoiseFilter)
eventSelection = cms.Sequence(offlineSelection)
eventSelectionHLT = cms.Sequence(hltBscMinBiasORBptxPlusORMinusFilter + offlineSelection)

"""
eventSelectionHLTHBVetoPlusAndMinus = cms.Sequence(eventSelectionHLT+hcalVetoHBPlusAndMinus)
eventSelectionHLTHBHEVetoPlusAndMinus = cms.Sequence(eventSelectionHLT+hcalVetoHBHEPlusAndMinus)
eventSelectionHLTSumEMaxHBPlusAndMinus4 = cms.Sequence(eventSelectionHLT+hcalVetoSumEMaxHBPlusAndMinus4)
eventSelectionHLTSumEMaxHBPlusAndMinus8 = cms.Sequence(eventSelectionHLT+hcalVetoSumEMaxHBPlusAndMinus8)
eventSelectionHLTSumEMaxHBPlusAndMinus12 = cms.Sequence(eventSelectionHLT+hcalVetoSumEMaxHBPlusAndMinus12)
eventSelectionHLTSumEMaxHBPlusAndMinus16 = cms.Sequence(eventSelectionHLT+hcalVetoSumEMaxHBPlusAndMinus16)
"""

#-------------------------------------------
# Sequences
tracks = cms.Sequence(analysisTracks*
                      selectTracksAssociatedToPV)

pfCandidates = cms.Sequence(pfCandidateNoiseThresholds* 
                            etaMaxPFCands+etaMinPFCands)

edmDump = cms.Sequence(hcalActivitySummary+hcalActivitySummaryScale090+hcalActivitySummaryScale092+
                       hcalActivitySummaryScale095+hcalActivitySummaryScale098+
                       hcalActivitySummaryScale102+hcalActivitySummaryScale105+
                       hcalActivitySummaryScale108+hcalActivitySummaryScale110+
                       edmNtupleEtaMax+edmNtupleEtaMin)
#-------------------------------------------
analysisSequences = cms.Sequence(tracks*pfCandidates*edmDump)
#-------------------------------------------