#include <chrono>

#include "TError.h"
#include "TH1F.h"

#include "QuickAnaHPC/AnalysisAlg.h"

#include "CxxUtils/make_unique.h"
#include "EventLoop/Job.h"
#include "EventLoop/StatusCode.h"
#include "EventLoop/Worker.h"
#include "QuickAna/QuickAna.h"
#include "PATInterfaces/SystematicsUtil.h"

// This is needed to distribute the algorithm to the workers
// Is that really true...?
ClassImp(AnalysisAlg)

//-----------------------------------------------------------------------------
// Constructor
//-----------------------------------------------------------------------------
AnalysisAlg::AnalysisAlg()
  : doSystematics(true), m_lastEvent(0)
{
}

//-----------------------------------------------------------------------------
// Configure job for this algorithm
//-----------------------------------------------------------------------------
EL::StatusCode AnalysisAlg::setupJob(EL::Job& job)
{
  // Tell the job I need xAOD access
  job.useXAOD();
  return EL::StatusCode::SUCCESS;
}

//-----------------------------------------------------------------------------
// Initialize after input files are connected
//-----------------------------------------------------------------------------
EL::StatusCode AnalysisAlg::initialize()
{
  // Initialize QuickAna
  auto quickAna = CxxUtils::make_unique<ana::QuickAna>("quickana");
  quickAna->setConfig(*this);
  if(quickAna->initialize().isFailure())
    return EL::StatusCode::FAILURE;

  // Setup systematics
  if(doSystematics) {
    auto sysList =
      CP::make_systematics_vector( quickAna->recommendedSystematics() );
    if(quickAna->setSystematics(sysList).isFailure())
      return EL::StatusCode::FAILURE;
  }

  // Book some histograms for each systematic
  for(auto& sys : quickAna->systematics()) {
    std::string sysName = sys.empty() ? "Nominal" : sys.name();

    // Electron kinematics
    book( TH1F(("el_n_"+sysName).c_str(), "Electron multiplicity", 5, 0, 5) );
    book( TH1F(("el_pt_"+sysName).c_str(), "Electron PT", 50, 0, 500) );
    book( TH1F(("el_eta_"+sysName).c_str(), "Electron eta", 10, -2.5, 2.5) );

    // Muon kinematics
    book( TH1F(("mu_n_"+sysName).c_str(), "Muon multiplicity", 5, 0, 5) );
    book( TH1F(("mu_pt_"+sysName).c_str(), "Muon PT", 50, 0, 500) );
    book( TH1F(("mu_eta_"+sysName).c_str(), "Muon eta", 10, -2.5, 2.5) );

    // Tau kinematics
    book( TH1F(("tau_n_"+sysName).c_str(), "Tau multiplicity", 5, 0, 5) );
    book( TH1F(("tau_pt_"+sysName).c_str(), "Tau PT", 50, 0, 500) );
    book( TH1F(("tau_eta_"+sysName).c_str(), "Tau eta", 10, -2.5, 2.5) );

    // Jet kinematics
    book( TH1F(("jet_n_"+sysName).c_str(), "Jet multiplicity", 5, 0, 5) );
    book( TH1F(("jet_pt_"+sysName).c_str(), "Jet PT", 50, 0, 500) );
    book( TH1F(("jet_eta_"+sysName).c_str(), "Jet eta", 10, -2.5, 2.5) );

    // MET
    book( TH1F(("met_"+sysName).c_str(), "MET", 50, 0, 500) );
  }

  m_quickAna = std::move(quickAna);
  return EL::StatusCode::SUCCESS;
}

//-----------------------------------------------------------------------------
// Process one event
//-----------------------------------------------------------------------------
EL::StatusCode AnalysisAlg::execute()
{
  // Printouts for progress and processing rate
  static int i = 0;
  const int freq = 100;
  static auto lastTime = std::chrono::steady_clock::now();
  if((i % freq) == 0) {
    typedef std::chrono::duration<float> fsec;
    auto currentTime = std::chrono::steady_clock::now();
    fsec diffTime = currentTime - lastTime;
    float rate = float(freq) / diffTime.count();
    lastTime = currentTime;
    Info("AnalysisAlg::execute", "Entry %i, %f evts/s", i, rate);
  }
  i++;

  // Workaround for duplicate successive events issue.
  // Compare event number to last one and skip if they're the same.
  auto evtStore = wk()->xaodEvent();
  const xAOD::EventInfo* evtInfo = nullptr;
  if(evtStore->retrieve(evtInfo, "EventInfo").isFailure())
    return EL::StatusCode::FAILURE;
  if(m_lastEvent == evtInfo->eventNumber()) {
    Warning("AnalysisAlg::execute", "Skipping duplicate event %llu at entry %i",
            m_lastEvent, i);
    return EL::StatusCode::SUCCESS;
  }
  m_lastEvent = evtInfo->eventNumber();

  // Loop over systematics
  for(auto& sys : m_quickAna->systematics()) {
    if(m_quickAna->applySystematicVariation(sys) != CP::SystematicCode::Ok)
      return EL::StatusCode::FAILURE;
    std::string sysName = sys.empty() ? "Nominal" : sys.name();

    // Run QuickAna for current event
    if(m_quickAna->process().isFailure())
      return EL::StatusCode::FAILURE;

    SG::AuxElement::ConstAccessor<ana::SelectType> isSelected("ana_select");
    const float invGeV = 0.001; // unit conversion
    const float weight = m_quickAna->weight();

    // Fill electron kinematics
    unsigned nEle = 0;
    for(auto electron : *m_quickAna->electrons()) {
      if(isSelected(*electron)) {
        hist("el_pt_"+sysName)->Fill( electron->pt()*invGeV, weight );
        hist("el_eta_"+sysName)->Fill( electron->eta() );
        ++nEle;
      }
    }
    hist("el_n_"+sysName)->Fill(nEle, weight);

    // Fill muon kinematics
    unsigned nMu = 0;
    for(auto muon : *m_quickAna->muons()) {
      if(isSelected(*muon)) {
        hist("mu_pt_"+sysName)->Fill( muon->pt()*invGeV, weight );
        hist("mu_eta_"+sysName)->Fill( muon->eta(), weight );
        ++nMu;
      }
    }
    hist("mu_n_"+sysName)->Fill(nMu, weight);

    // Fill tau kinematics
    unsigned nTau = 0;
    for(auto tau : *m_quickAna->taus()) {
      if(isSelected(*tau)) {
        hist("tau_pt_"+sysName)->Fill( tau->pt()*invGeV, weight );
        hist("tau_eta_"+sysName)->Fill( tau->eta(), weight );
        ++nTau;
      }
    }
    hist("tau_n_"+sysName)->Fill(nTau, weight);

    // Fill jet kinematics
    unsigned nJet = 0;
    for(auto jet : *m_quickAna->jets()) {
      if(isSelected(*jet)) {
        hist("jet_pt_"+sysName)->Fill( jet->pt()*invGeV, weight );
        hist("jet_eta_"+sysName)->Fill( jet->eta(), weight );
        ++nJet;
      }
    }
    hist("jet_n_"+sysName)->Fill(nJet, weight);

    // Fill MET kinematics
    hist("met_"+sysName)->Fill( m_quickAna->met()->met()*invGeV, weight );

  }

  return EL::StatusCode::SUCCESS;
}

//-----------------------------------------------------------------------------
// Finalize
//-----------------------------------------------------------------------------
EL::StatusCode AnalysisAlg::finalize()
{
  return EL::StatusCode::SUCCESS;
}
