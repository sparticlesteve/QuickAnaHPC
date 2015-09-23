#ifndef QuickAnaHPC_AnalysisAlg_H
#define QuickAnaHPC_AnalysisAlg_H

#include <memory>

#include "EventLoop/Algorithm.h"
#include "QuickAna/Configuration.h"
#include "QuickAna/IQuickAna.h"

/// @brief Simple EL algorithm running QuickAna
///
/// NOTE: variables that don't get filled at submission time should be
/// protected from being send from the submission node to the worker
/// node (done by the //!).
///
class AnalysisAlg : public EL::Algorithm, public ana::Configuration
{

  public:

    /// Standard constructor
    AnalysisAlg();

    /// @brief Setup the job to use this algorithm.
    ///
    /// Here you put code that sets up the job on the submission object
    /// so that it is ready to work with your algorithm, e.g. you can
    /// request the D3PDReader service or add output files.  Any code you
    /// put here could instead also go into the submission script.  The
    /// sole advantage of putting it here is that it gets automatically
    /// activated/deactivated when you add/remove the algorithm from your
    /// job, which may or may not be of value to you.
    virtual EL::StatusCode setupJob(EL::Job& job);

    /// @brief Pre-initialize the algorithm.
    ///
    /// Here you do everything that needs to be done at the very
    /// beginning on each worker node, e.g. create histograms and output
    /// trees.  This method gets called before any input files are
    /// connected.
    //virtual EL::StatusCode histInitialize();

    /// @brief Initialize the algorithm.
    ///
    /// Here you do everything that you need to do after the first input
    /// file has been connected and before the first event is processed,
    /// e.g. create additional histograms based on which variables are
    /// available in the input files.  You can also create all of your
    /// histograms and trees in here, but be aware that this method
    /// doesn't get called if no events are processed.  So any objects
    /// you create here won't be available in the output if you have no
    /// input events.
    virtual EL::StatusCode initialize();

    /// @brief Process one event
    ///
    /// Here you do everything that needs to be done on every single
    /// events, e.g. read input variables, apply cuts, and fill
    /// histograms and trees.  This is where most of your actual analysis
    /// code will go.
    virtual EL::StatusCode execute();

    /// @brief Finalize the algorithm
    ///
    /// This method is the mirror image of initialize(), meaning it gets
    /// called after the last event has been processed on the worker node
    /// and allows you to finish up any objects you created in
    /// initialize() before they are written to disk.  This is actually
    /// fairly rare, since this happens separately for each worker node.
    /// Most of the time you want to do your post-processing on the
    /// submission node after all your histogram outputs have been
    /// merged.  This is different from histFinalize() in that it only
    /// gets called on worker nodes that processed input events.
    virtual EL::StatusCode finalize();

    /// @brief Finalize the algorithm
    ///
    /// This method is the mirror image of histInitialize(), meaning it
    /// gets called after the last event has been processed on the worker
    /// node and allows you to finish up any objects you created in
    /// histInitialize() before they are written to disk.  This is
    /// actually fairly rare, since this happens separately for each
    /// worker node.  Most of the time you want to do your
    /// post-processing on the submission node after all your histogram
    /// outputs have been merged.  This is different from finalize() in
    /// that it gets called on all worker nodes regardless of whether
    /// they processed input events.
    //virtual EL::StatusCode histFinalize();

    /// Declare ROOT dictionary methods
    ClassDef(AnalysisAlg, 1);

  private:

    /// QuickAna analysis tool.
    std::unique_ptr<ana::IQuickAna> m_quickAna; //!

};

#endif
