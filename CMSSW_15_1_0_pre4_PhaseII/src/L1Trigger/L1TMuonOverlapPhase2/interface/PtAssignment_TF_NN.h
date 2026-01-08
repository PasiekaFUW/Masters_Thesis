/*
 * PtAssignment_TF_NN.h
 *
 *  Created on: Thu Jun 10 10:42:22 CEST 2021
 *      Author: akalinow
 */

#ifndef INTERFACE_PTASSIGNMENT_TF_NN_H_
#define INTERFACE_PTASSIGNMENT_TF_NN_H_

#include "L1Trigger/L1TMuonOverlapPhase1/interface/Omtf/PtAssignmentBase.h"
#include "L1Trigger/L1TMuonOverlapPhase1/interface/Omtf/AlgoMuon.h"

#include "PhysicsTools/TensorFlow/interface/TensorFlow.h"
/*
 Pt assignment using NN trained with TensorFlow
 */
class PtAssignment_TF_NN: public PtAssignmentBase{
public:

  PtAssignment_TF_NN(const edm::ParameterSet& edmCfg, const OMTFConfiguration* omtfConfig); 

  std::vector<float> getPts(AlgoMuons::value_type& algoMuon,
    std::vector<std::unique_ptr<IOMTFEmulationObserver> >& observers) override;

private:

  void initializeModel(const std::string & model_path);

  tensorflow::GraphDef* tfGraph{0};
  tensorflow::Session* tfSession{0};

  tensorflow::SessionOptions session_options;
  tensorflow::RunOptions run_options;
  tensorflow::SavedModelBundle model;
  std::string inputs_name{""};
  std::string outputs_name{""};
};

#endif /* INTERFACE_PTASSIGNMENT_TF_NN_H_ */
