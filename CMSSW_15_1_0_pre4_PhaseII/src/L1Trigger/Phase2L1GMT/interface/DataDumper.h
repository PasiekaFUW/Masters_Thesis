/*
 * DataDumper.h
 *
 *  Created on: Nov 5, 2021
 *      Author: kbunkow
 */

#ifndef INTERFACE_DATADUMPER_H_
#define INTERFACE_DATADUMPER_H_

#include "L1Trigger/Phase2L1GMT/interface/PreTrackMatchedMuon.h"
#include "SimDataFormats/Associations/interface/TTTrackAssociationMap.h"
#include "FWCore/Utilities/interface/EDGetToken.h"
#include "FWCore/Framework/interface/Event.h"
#include "TFile.h"
#include "TTree.h"

namespace Phase2L1GMT {

constexpr unsigned int tfLayersCnt = 5;
struct TrackMatchedMuonRecord {

  //from trackingParticle
  float tpPt = 0, tpEta = 0, tpPhi = 0;
  short tpCharge = 0;
  char type = 0;

  //0 - no match, 1 - very loose, 2 - loose , 3
  char matching = 0;

  //from ttTrack
  uint tttCharge = 0;
  uint tttPt = 0;
  int tttEta = 0;
  int tttPhi = 0;
  int tttZ0 = 0;
  int tttD0 = 0;

  //from GMT
  uint beta = 0;
  bool isGlobal = 0;
  uint quality = 0;

  std::vector<Phase2L1GMT::propagation_t> propagatedStates;

  std::vector<unsigned char> deltaCoords1;
  std::vector<unsigned char> deltaCoords2;
  std::vector<unsigned char> deltaEta1;
  std::vector<unsigned char> deltaEta2;
  std::vector<char> stubTiming;

  TrackMatchedMuonRecord(): propagatedStates(tfLayersCnt),
                            deltaCoords1(tfLayersCnt), deltaCoords2(tfLayersCnt), 
                            deltaEta1(tfLayersCnt), deltaEta2(tfLayersCnt),
                            stubTiming(tfLayersCnt) {}

  void reset(){
    tpPt = 0;
    tpEta = 0;
    tpPhi = 0;
    tpCharge = 0;
    type = 0;
    matching = 0;
    tttCharge = 0;
    tttPt = 0;
    tttEta = 0;
    tttPhi = 0;
    tttZ0 = 0;
    tttD0 = 0;
    beta = 0;
    isGlobal = 0;
    quality = 0;
    for (auto& state : propagatedStates) state = propagation_t();
    for (auto& coord : deltaCoords1) coord = 0;
    for (auto& coord : deltaCoords2) coord = 0;
    for (auto& eta : deltaEta1) eta = 0;
    for (auto& eta : deltaEta2) eta = 0;
    for (auto& timing : stubTiming) timing = 0;
  }
};


class PreTrackMatchedMuonProcessor {
public:
  PreTrackMatchedMuonProcessor() {};
  virtual ~PreTrackMatchedMuonProcessor() {};

  virtual void process(PreTrackMatchedMuon& preTrackMatchedMuon) = 0;
};

class DataDumper: public PreTrackMatchedMuonProcessor {
public:
  DataDumper(const edm::EDGetTokenT< TTTrackAssociationMap< Ref_Phase2TrackerDigi_ > >& ttTrackMCTruthToken,
             const edm::EDGetTokenT< std::vector< TrackingParticle > >& trackingParticleToken, bool dumpToRoot);

  virtual ~DataDumper(){};

  void getHandles(const edm::Event& event);

  void process(PreTrackMatchedMuon& preTrackMatchedMuon) override;

private:
  void initializeTTree();

  edm::EDGetTokenT< TTTrackAssociationMap< Ref_Phase2TrackerDigi_ > > ttTrackMCTruthToken;
  edm::Handle< TTTrackAssociationMap< Ref_Phase2TrackerDigi_ > > mcTruthTTTrackHandle;

  edm::EDGetTokenT< std::vector< TrackingParticle > > trackingParticleToken;
  edm::Handle< std::vector< TrackingParticle > > trackingParticleHandle;

  std::vector<edm::Ptr< TrackingParticle > > muonTrackingParticles;
  bool muonTrackingParticlesFilled = false;

  TTree* rootTree = nullptr;

  TrackMatchedMuonRecord record;

  unsigned int evntCnt = 0;
};

} /* namespace Phase2L1GMT */

#endif /* INTERFACE_DATADUMPER_H_ */
