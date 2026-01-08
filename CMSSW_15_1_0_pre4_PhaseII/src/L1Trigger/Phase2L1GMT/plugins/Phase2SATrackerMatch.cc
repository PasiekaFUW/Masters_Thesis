#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/ConsumesCollector.h"
#include "DataFormats/L1TMuonPhase2/interface/TrackerMuon.h"
#include "DataFormats/L1TMuonPhase2/interface/SAMuon.h"
#include <iostream>
#include <vector>



class Phase2SATrackerMatch : public edm::stream::EDProducer<> {
public:
  explicit Phase2SATrackerMatch(const edm::ParameterSet&);
  ~Phase2SATrackerMatch() override;

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

private:
  void beginJob();

  int findBestTrackerMuon(const l1t::SAMuon & samuon, 
                          const std::vector<l1t::TrackerMuon>& trackerMuons) const;

  void produce(edm::Event&, const edm::EventSetup&) override;
  void endJob() ;
  bool verbose_;

  edm::EDGetTokenT<std::vector<l1t::SAMuon>> samuonToken_;
  edm::EDGetTokenT<std::vector<l1t::TrackerMuon>> trackerMuonToken_;
};

// Constructor: Initializes the Phase2SATrackerMatch class
Phase2SATrackerMatch::Phase2SATrackerMatch(const edm::ParameterSet& iConfig)
    : verbose_(iConfig.getUntrackedParameter<bool>("verbose", false)),
      samuonToken_(consumes<std::vector<l1t::SAMuon>>(iConfig.getParameter<edm::InputTag>("samuons"))),
      trackerMuonToken_(consumes<std::vector<l1t::TrackerMuon>>(iConfig.getParameter<edm::InputTag>("trackerMuons"))) {
  // Register the product
  produces<std::vector<l1t::SAMuon>>("SAMuonsWithCommonStubInfo").setBranchAlias("SAMuonsWithCommonStubInfo");
}

// Destructor: Cleans up any resources used by the Phase2SATrackerMatch class
Phase2SATrackerMatch::~Phase2SATrackerMatch() {}

// Called once at the beginning of the job
void Phase2SATrackerMatch::beginJob() {}

int Phase2SATrackerMatch::findBestTrackerMuon(const l1t::SAMuon & samuon, 
                                              const std::vector<l1t::TrackerMuon>& trackerMuons) const {

  samuon.print();
  LogDebug("SAMuon") << "SAMuon number of stubs: " << samuon.stubs().size() << std::endl;

  int bestMatchCount = 0;
  
  for (auto& trackerMuon : trackerMuons) {

    int commonStubCount = 0;
    trackerMuon.print();
    LogDebug("TrackerMuon") << "TrackerMuon number of stubs: " << trackerMuon.stubs().size() << std::endl;

    for (auto& samuonStub : samuon.stubs()){

         LogDebug("SAMuon") << "SAMuon stub: " << std::endl;
         samuonStub->print();

         LogDebug("TrackerMuon") << "TrackerMuon stubs: " << std::endl;
        for (auto& trackerMuonStub : trackerMuon.stubs()) {

          trackerMuonStub->print();

            bool tfLayerMatch = (samuonStub->tfLayer() == trackerMuonStub->tfLayer());
            bool bxNumMatch = (samuonStub->bxNum() == trackerMuonStub->bxNum());
            bool typeMatch = (samuonStub->type() == trackerMuonStub->type());
            bool qualityMatch = true; //hybrid stubs have quality fixed to 3 (samuonStub->quality() == trackerMuonStub->quality());
            bool etaQualityMatch = (samuonStub->etaQuality() == trackerMuonStub->etaQuality());

            LogDebug("SAMuon") << "tfLayerMatch: " << tfLayerMatch
                               << ", bxNumMatch: " << bxNumMatch
                               << ", typeMatch: " << typeMatch
                               << ", qualityMatch: " << qualityMatch
                               << ", etaQualityMatch: " << etaQualityMatch
                               << std::endl;

            if (!(tfLayerMatch && bxNumMatch && typeMatch && qualityMatch && etaQualityMatch)) continue;

            ///etaQuality:
            /// 0 = no eta coordinate
            /// 1 = eta1 coordinate only
            /// 2 = eta2 coordinates only
            /// 3 = both eta1 and eta2 coordinates

            ///type==0 && etaQuality==1 - DT/RPC with eta1, coord1
            ///type==0 && etaQuality==2 - RPC only, with eta2, coord2
            ///type==0 && etaQuality==3 - RPC+CSC with eta1, coord1, eta2, coord2

            ///type==1 && etaQuality==0 - DT coarse eta coordinate
            ///type==1 && etaQuality==1 - DT with single eta coordinate
            ///type==1 && etaQuality==3 - DT with two eta coordinates

            int samuonStubCoord1 = samuonStub->type()==1 ? samuonStub->coord1()/256: samuonStub->coord1(); //use the same scale as in hybrid stubs
            int samuonStubCoord2 = samuonStub->type()==1 ? samuonStub->coord2()/256: samuonStub->coord2(); //use the same scale as in hybrid stubs

            LogDebug("SAMuon") << "samuonStubCoord1: " << samuonStubCoord1
                               << ", samuonStubCoord2: " << samuonStubCoord2
                               << std::endl;

            bool eta1Valid = samuonStub->type() == 1 || (samuonStub->etaQuality() == 1 || samuonStub->etaQuality() == 3);
            bool eta2Valid = (samuonStub->etaQuality() == 2 || samuonStub->etaQuality() == 3);

            bool coord1Valid = samuonStub->type() == 1 || eta1Valid;
            bool coord2Valid = samuonStub->type() == 1 || eta2Valid;
  
            bool coord1Match = (samuonStubCoord1 == trackerMuonStub->coord1());
            bool coord2Match = (samuonStubCoord2 == trackerMuonStub->coord2());
            
            bool eta1Match = (samuonStub->eta1() == trackerMuonStub->eta1());
            bool eta2Match = (samuonStub->eta2() == trackerMuonStub->eta2());

            int matchCount = coord1Match*coord1Valid + 
                             coord2Match*coord2Valid + 
                             eta1Match*eta1Valid + 
                             eta2Match*eta2Valid;
            
            commonStubCount += matchCount == (coord1Valid + coord2Valid + eta1Valid + eta2Valid);

            LogDebug("SAMuon") << "eta1Valid: " << eta1Valid
                               << ", eta2Valid: " << eta2Valid
                               << ", coord1Valid: " << coord1Valid
                               << ", coord2Valid: " << coord2Valid
                               << ", coord1Match: " << coord1Match
                               << ", coord2Match: " << coord2Match
                               << ", eta1Match: " << eta1Match
                               << ", eta2Match: " << eta2Match
                               << ", matchCount: " << matchCount
                               << ", commonStubCount: " << commonStubCount
                               << " bestMatchCount: " << bestMatchCount
                               <<std::endl;
        }

            if(commonStubCount > bestMatchCount) {
                bestMatchCount = commonStubCount;
          }
        }
      }
    return bestMatchCount;
}
//////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////



// Called for each event to produce the output
void Phase2SATrackerMatch::produce(edm::Event& iEvent, const edm::EventSetup& iSetup) {
  // Retrieve SAMuons from the event
  edm::Handle<std::vector<l1t::SAMuon>> samuons;
  iEvent.getByToken(samuonToken_, samuons);

  // Retrieve TrackerMuons from the event
  edm::Handle<std::vector<l1t::TrackerMuon>> trackerMuons;
  iEvent.getByToken(trackerMuonToken_, trackerMuons);

  // Vector to store SAMuons with common stub information
  std::vector<l1t::SAMuon> samuonsWithCommonStubInfo;

  LogDebug("SAMuon") << "Number of SAMuons: " << samuons->size()<<std::endl;

  int commonStubCount = 0;
  for (const auto& samuon : *samuons){
    commonStubCount = findBestTrackerMuon(samuon, *trackerMuons);
    l1t::SAMuon newSAmuon = {samuon};
    newSAmuon.setCommonStubCount(commonStubCount);
  //newSAmuon.setCommonStubQuality(commonQualitySum);
    newSAmuon.setTotalStubCount(samuon.stubs().size());
  //newSAmuon.setTotalStubQuality(totalQualitySum);
    samuonsWithCommonStubInfo.push_back(newSAmuon);
  }

  // Create and put the output collections
  auto outputSAMuonsWithCommonStubInfo = std::make_unique<std::vector<l1t::SAMuon>>(samuonsWithCommonStubInfo);
  iEvent.put(std::move(outputSAMuonsWithCommonStubInfo), "SAMuonsWithCommonStubInfo");
}

// Called once at the end of the job
void Phase2SATrackerMatch::endJob() {}

// Fills descriptions for the module
void Phase2SATrackerMatch::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;
  desc.add<edm::InputTag>("samuons", edm::InputTag("samuons"));
  desc.add<edm::InputTag>("trackerMuons", edm::InputTag("trackerMuons"));
  desc.addUntracked<bool>("verbose", false);
  descriptions.add("phase2SATrackerMatch", desc);
}

// Define this as a plug-in
DEFINE_FWK_MODULE(Phase2SATrackerMatch);