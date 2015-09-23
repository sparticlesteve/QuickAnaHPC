#include "EventLoop/Job.h"
#include "EventLoop/StatusCode.h"
#include "EventLoop/Worker.h"
#include "QuickAnaHPC/AnalysisAlg.h"

// This is needed to distribute the algorithm to the workers
// Is that really true...?
ClassImp(AnalysisAlg)

//-----------------------------------------------------------------------------
// Constructor
//-----------------------------------------------------------------------------
AnalysisAlg::AnalysisAlg()
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
  return EL::StatusCode::SUCCESS;
}

//-----------------------------------------------------------------------------
// Process one event
//-----------------------------------------------------------------------------
EL::StatusCode AnalysisAlg::execute()
{
  return EL::StatusCode::SUCCESS;
}

//-----------------------------------------------------------------------------
// Finalize
//-----------------------------------------------------------------------------
EL::StatusCode AnalysisAlg::finalize()
{
  return EL::StatusCode::SUCCESS;
}
