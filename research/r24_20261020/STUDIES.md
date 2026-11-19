# R24: Twenty-four bounded research investigations

Created 20 October 2026. This is a new prospective selection, not a claim that earlier projects have been completed. The owner's uploaded Ultimate Individual Research Project Pipeline governs this work. Historical negative, invalid, inconclusive and protected results remain authoritative and unchanged. Worldcastr is excluded entirely.

## Honest state and common contract

Four development implementations exist in `core.py` and `run_development.py`: 01, 05, 09 and 13. Their code has not yet been scientifically run. The other twenty investigations are specified below but are not implemented. An initial literature screen is not exhaustive novelty verification. None of the twenty-four has passed the final evidence, independent-verification or release gate. Some questions may merge into one paper after overlap review; twenty-four questions do not imply twenty-four independent publishable contributions.

Each study uses a separate version identity R24-20261020-XX-v0.1. No historical project's hypothesis or result is overwritten. Proposed repository homes below are lineage pointers only, not permission to alter those repositories or assertions that the new code is already integrated there. New shared development code is isolated in Percy-Projects.

For substantial runs, CUDA is mandatory. The committed runner executes DEVELOPMENT only and fails rather than silently using CPU. No Kaggle run, GPU runtime estimate, effect size, positive result or final paper exists for this wave at registration. New paid compute is not authorized by this package. Timing, hardware availability and remaining quota must be measured before assigning a full study budget. The implementation budget is bounded to this version; a changed scientific mechanism requires a recorded successor.

For each candidate, complete its nearest-method reproduction and data-license/provenance review before an IDEA READY judgment. Calibrate models only on development data, and use independent experimental units appropriate to the study, not correlated time steps as replicates. Pilot seeds 0,1,2 are engineering/development only. Confirmatory replication counts must be chosen from a precision analysis before outcomes, with 10 independent fits or task units as an initial floor rather than a power guarantee. Freeze the code, data versions, disjoint group/time splits, endpoint, practical margin, controls, candidate-selection budget, exclusion rule, runtime cap, multiplicity family and analysis before a separate protected run. A prospective 2% relative error improvement is a starting engineering target, not a universal scientifically meaningful margin; deviations must be justified before confirmation. Holm correction covers the twenty-four primary claims if they are tested as one portfolio; selective publication of the best subset is prohibited. Within-study ablations are secondary unless separately registered.

Terminal outcomes are SUPPORTED, MIXED, NEGATIVE or INCONCLUSIVE after validity review; INVALID remains an auditable run state requiring a recorded correction. No stopping rule says 'continue until positive'. Final release requires raw evidence, reproducible analysis, manuscripts with scope-correct conclusions, authorship/license approval and an independent review. None of those terminal outcomes is assigned prematurely here.

## A. Causal and decision-aware financial learning

### 01. Intervention-Checked Reservoirs (ICR)

**Question and mechanism.** Do environment-gradient-moment constraints on a fixed reservoir readout improve prediction under interventions on a spurious measurement mechanism? For environment e, define G_e=X_e^T X_e/n_e and c_e=X_e^T y_e/n_e. Minimize mean_e MSE_e(w)+lambda||w||^2+gamma mean_e||(G_e-Gbar)w-(c_e-cbar)||^2. A positive ridge makes the quadratic problem uniquely solvable. This is an invariance estimator, not a general causal-identification result.

**Data and controls.** Start with the fully specified lagged SCM in `finance_scm`; hold latent dynamics fixed while changing the proxy coefficient. Independent trajectories form train, validation and development-OOD populations. Compare the identical reservoir without the penalty and a raw-lag ridge model, with nine candidate fits per tuned arm. Before a financial claim, add conditional-independence/structural-inference baselines, a well-tuned recurrent model, hidden-confounder stress tests and point-in-time licensed market data with purged chronological splits and costs.

**Endpoint and falsifier.** Trajectory-level normalized prediction error under a predeclared intervention, with a margin calibrated before confirmation. Failure to beat the strongest independently tuned control, or gain vanishing when causal information is matched, rejects the proposed benefit. Hidden confounding can invalidate causal interpretation even when forecasting improves.

**Novelty/flaw repair.** Reservoir causal inference and invariant prediction already exist [S01,S02,S03]. The candidate contribution is a bounded intervention/measurement-noise tradeoff, not 'reservoirs discover causality'. Wrong causal language -> nonidentification -> critical -> separate simulated interventions from observational market evidence -> report edge-recovery only when ground truth and assumptions justify it. State: development mechanism and runner implemented, unexecuted. Lineage: the user's financial-causation reservoir idea; not a replacement for FREM.

### 02. Mechanism-Localized Regime Detection (MLRD)

**Question and mechanism.** Can residual changes in a fitted lagged structural model distinguish changes to one conditional mechanism from changes only in marginal volatility? Fit conditional predictors on a training window, retain residual features, and compare change scores on residual distributions against raw covariance change. A sparse localization rule must output the affected conditional equation or abstain; time t cannot use later regime labels.

**Data and controls.** Generate independent multivariate SCMs with separately controlled coefficient changes, innovation-variance changes and latent-confounder changes. Split by entire graph and chronological segment. Compare CUSUM on raw/residual features, a covariance detector, PCMCI-style conditional modeling after reproduction, and reservoir-free predictors with matched information.

**Endpoint and falsifier.** Detection delay at a fixed false-alarm budget, with localization accuracy secondary. A detector that simply flags every volatility jump or achieves low delay by raising false alarms fails. Flaw -> persistent forecast misspecification can mimic mechanism change -> high -> include stationary but misspecified controls and an abstention category -> demonstrate calibrated false alarms on held-out graphs. Related reservoir structure inference [S02,S03] prevents a generic causal-network novelty claim. State: specified, not implemented.

### 03. Regime-Conditional Coverage Audit (RCCA)

**Question and mechanism.** Does a trailing, strictly causal regime descriptor improve the worst-regime calibration/width tradeoff beyond adaptive conformal inference? Maintain separate residual score pools with shrinkage toward a global pool; update only after the outcome becomes available. Separate marginal time-average coverage from any conditional coverage claim.

**Data and controls.** Synthetic volatility/mean shifts followed by a licensed, fixed-vintage market panel. Fit forecasters on training windows, calibrate on later windows and evaluate on later nonoverlapping episodes. Compare split conformal, rolling conformal, adaptive conformal inference and bias-corrected ACI. Regime detection itself must use past data only.

**Endpoint and falsifier.** Worst preregistered-regime coverage deficit subject to an interval-width ceiling. Infinite or excessively wide intervals do not count as success. Failure to improve the coverage-width frontier rejects the mechanism. Flaw -> sparse regimes and adaptive conditioning -> critical -> minimum group sizes, fallback pools and explicitly limited coverage statements -> simulation counterexamples plus interval-score comparisons. Existing ACI and bias-correction methods [S04,S05] narrow the contribution to the audit and controlled grouping rule. State: specified, not implemented.

### 04. Cost-Bounded Trading Abstention (CBTA)

**Question and mechanism.** Can a forecast system abstain when a lower confidence bound on incremental utility fails to exceed spread, fees and estimated impact? The policy chooses trade only when LCB(benefit)-UCB(cost)>0, under a fixed turnover and risk budget. The study concerns decision calibration, not a promise of profitable trading.

**Data and controls.** First use a simulator with known execution costs, then admit licensed point-in-time data including delistings and availability times. Compare no-trade, equal-risk passive exposure, fixed-threshold abstention, calibrated probabilistic trading and a cost-aware baseline. Split by date; purge overlapping label horizons; freeze transaction-cost sensitivity ranges.

**Endpoint and falsifier.** Net utility at matched risk and coverage, with turnover and worst-case cost stress tests. If gains disappear at the predeclared plausible cost ceiling or merely reflect lower risk, reject the advantage. Flaw -> underestimated impact/survivorship -> critical -> conservative costs and full universe accounting -> audited fills or explicit simulation-only scope. Adaptive uncertainty [S04,S05] is prior machinery, not the new contribution. State: specified, not implemented; no live trading is authorized.

## B. Physical computation and scientific dynamics

### 05. Power-Matched Adaptive Noise Reservoirs (PANR)

**Question and mechanism.** Can state-dependent diffusion improve a driven physical reservoir's delayed nonlinear reconstruction when expected injected power is matched? The current simulator is a periodic double-well lattice: dh=(h-h^3+kappa Lap(h)+b u)dt+sigma g(h)sqrt(dt)epsilon. Normalize g to spatial RMS one. The learned component is bounded validation selection of gate shape and noise amplitude, not an unspecified 'intelligent noise' network.

**Data and controls.** Independent scalar input sequences with a declared delayed nonlinear target, independent initial/reset trajectories and a shifted input-amplitude evaluation. Compare tuned zero-noise and uniform-noise models, plus an exact selected-amplitude gate-off control. Each tuned arm receives nine candidate fits. Add matched ESN/linear autoregression and solver-refinement controls before full study approval.

**Endpoint and falsifier.** Normalized reconstruction error, with expected and realized noise power both retained. A gain that disappears with power matching, stronger no-noise tuning, finer integration or observation-noise controls fails. Flaw -> numerical noise mistaken for physical benefit -> critical -> distinguish process noise from measurement noise; verify discretization and identical substrate seeds -> convergence and ablation evidence.

Noise benefits and stochastic reservoirs are established topics [S06,S07,S08]; the proposed boundary is adaptive gating under matched power and substrate shift. This is not yet turbulence, plasma or device evidence. State: development mechanism and runner implemented, unexecuted. Existing catalogue noise-gating candidates remain predecessors rather than newly discovered ideas.

### 06. Conservation-Bounded Residual Corrections (CBRC)

**Question and mechanism.** Can a learned correction be useful when projected into the nullspace of a discretized conservation operator and bounded by a residual trust region? For base update u+, compute delta=P_null(C) r_theta(u), then scale it to satisfy a predeclared stability/energy bound. Projection enforces only the specified discrete invariant; it does not prove accuracy or continuous physical fidelity.

**Data and controls.** A verified finite-volume advection/diffusion benchmark and a later Burgers/PDEBench slice. Hold out initial-condition families and coefficients. Compare the base solver, projected random correction, unprojected learned correction, additional solver steps and additional training at the same budget.

**Endpoint and falsifier.** Long-horizon error subject to conservation and instability constraints. Improvement that vanishes against additional solver work or violates the stability constraint fails. Flaw -> projection alters boundary conditions or hides truncation error -> critical -> derive the discrete operator and perform manufactured-solution tests -> invariant, grid-refinement and wall-time evidence. This is a distinct possible APEN successor, not a rescue of its original equal-budget negative result. PDEBench [S09] is a benchmark, not validation. State: specified, not implemented.

### 07. Noise-Benefit Response Diagnostics (NBRD)

**Question and mechanism.** Can a training-only response statistic predict the sign of noise benefit on a genuinely unseen substrate? Estimate finite-difference derivatives of task loss with respect to noise power over a bounded development range, together with state-transition statistics. Fit a sign predictor across training substrates; test it on held-out substrate families without tuning the noise there.

**Data and controls.** Independent coupled-oscillator and double-well instances with known forcing/noise settings. Split by substrate, not windows. Compare always-zero noise, always-best-development amplitude, a direct small sweep given the same evaluation budget, and a feature-shuffled diagnostic.

**Endpoint and falsifier.** Regret relative to the permitted-budget oracle and calibration of predicted benefit signs. A diagnostic no better than spending its cost on direct evaluation fails. Flaw -> a local derivative need not predict finite-noise benefit -> high -> predeclare the radius and curvature counterexamples -> show where the certificate is invalid. Noise literature [S06,S08] already covers performance effects. This may merge with 05 unless cross-substrate prediction forms an independent contribution. State: specified, not implemented.

### 08. Finite-Memory Subgrid Closure (FMSC)

**Question and mechanism.** When unresolved dynamics matter, can a finite convolutional memory kernel improve a coarse solver at the same state/parameter budget? Model closure as sum_{j=0}^{L-1} K_j phi(u_{t-j}), optionally constrained by dissipativity, rather than simply adding hidden units to a Markov model.

**Data and controls.** A two-timescale system with known elimination structure, followed by coarse/fine PDE trajectory pairs. Hold out forcing and coefficient families. Compare a capacity-matched Markov closure, delay embedding, recurrent closure and a reproduced Mori-Zwanzig-inspired method.

**Endpoint and falsifier.** Coarse long-horizon error with stability and runtime constraints; a same-budget delay embedding matching the gain defeats a special-memory claim. Flaw -> higher temporal resolution leaks future fine states -> critical -> causal alignment and timestep audit -> unit tests and stored input/target windows. Non-Markovian/Mori-Zwanzig closures are prior art [S10,S11]; investigate a specific finite-budget stability tradeoff instead. State: specified, not implemented.

## C. Learning without global backpropagation

### 09. Blockwise Antithetic Forward Optimization (BAFO)

**Question and mechanism.** At a fixed number of function evaluations, does uniformly sampled blockwise two-sided perturbation improve the optimization/memory frontier over full-vector perturbation? For block b with inclusion probability p_b, use ghat=(L(theta+epsilon d_b)-L(theta-epsilon d_b))d_b/(2 epsilon p_b). The paired evaluations use identical data and randomness. This is finite-difference optimization, not forward-mode automatic differentiation.

**Data and controls.** A small teacher-student MLP is implemented for development. Compare full-vector antithetic updates and a reverse-mode reference with identical architecture, initialization and minibatches. Extend to fixed licensed benchmarks and a parameter-efficient pretrained model only after the pilot and baseline calibration pass.

**Endpoint and falsifier.** Quality versus wall-clock, function evaluations and peak memory, all reported separately. Equal calls alone are not equal compute. No broad advantage is supported if blockwise estimation only converges after more evaluations or an unfair learning-rate search. Flaw -> dimension-dependent variance and biased block selection -> high -> inverse-probability weighting and gradient-check counterexamples -> exact quadratic enumeration and nonquadratic tests.

MeZO, forward gradients and older zeroth-order methods are prior art [S12,S13]. Candidate novelty lies in a measurable block-allocation regime, not 'learning without backprop'. State: development mechanism and runner implemented, unexecuted.

### 10. Local Predictive Credit Transport (LPCT)

**Question and mechanism.** Can layer-local predictive targets propagate useful credit with a bounded number of local inference steps? Each block minimizes its own target mismatch with stop-gradient boundary states; a transport operator predicts the target correction sent to the preceding block. The graph of all gradient paths must be audited.

**Data and controls.** Teacher networks and one fixed image/classification benchmark with architecture held constant. Compare backpropagation, greedy local losses, predictive coding, forward-forward and random target feedback, with equal hyperparameter-search budgets.

**Endpoint and falsifier.** Accuracy versus full training cost including local inference. A gain requiring hidden global backpropagation, uncounted inference loops or extra labeled information fails. Flaw -> global gradients re-enter through target construction -> critical -> explicit detach and instrumentation -> per-parameter gradient-path tests. Predictive coding and temporal credit methods already address local learning [S14,S15]; the study must show a distinct bounded transport mechanism. State: specified, not implemented.

### 11. Error-Broadcast Rank Allocation (EBRA)

**Question and mechanism.** How much error-feedback rank is needed to train a layered network under a fixed communication budget? Broadcast a low-rank random or learned projection of output error, and allocate rank between layers using training-only sensitivity summaries. Count every communicated scalar and every pass.

**Data and controls.** Fixed small vision or sequence tasks with width/depth scaling. Compare direct feedback alignment, fixed-rank feedback, backpropagation and random rank allocation. Use identical architecture and an equal total feedback-rank constraint.

**Endpoint and falsifier.** Accuracy at a fixed communication and memory budget. Failure to beat a fixed-rank allocation, or success only when feedback learning uses an unreported global-gradient teacher, rejects the allocation claim. Flaw -> a learned feedback matrix adds hidden training cost -> high -> count amortization and out-of-family transfer -> total-cost curves. Local-learning literature [S14] is a starting anchor; direct-feedback-alignment nearest-method reproduction is still a gate. State: specified, not implemented; novelty review incomplete.

### 12. Meta-Learned Local Update Rules (MLLUR)

**Question and mechanism.** Can a small hypernetwork map local activation/error statistics to parameter updates that transfer to new widths and tasks? The update rule receives only a declared local information set. Meta-training may use backpropagation, but that cost must be included and the result cannot be described as globally backprop-free training overall.

**Data and controls.** Meta-train on a fixed collection of synthetic tasks and reserve task generators, widths and optimization horizons for evaluation. Compare SGD/Adam, learned optimizers with equivalent inputs, fixed local rules and a shuffled-statistics hypernetwork.

**Endpoint and falsifier.** Total-cost-adjusted adaptation loss across held-out tasks. No transfer beyond meta-training distributions, or a benefit erased by amortized meta-training cost, fails. Flaw -> meta-test leakage/task memorization -> critical -> generator-level splits and frozen meta-checkpoint -> hashes and unseen-task evaluation. Hypernetworks and initialization theory already exist [S16,S17]; the candidate is locality-constrained transferable update behavior. State: specified, not implemented.

## D. Memory, interventions and representation

### 13. Selective Memory Necessity and Substitution (SMNS)

**Question and mechanism.** Does a memory model's apparent retrieval correspond to selective use of the relevant stored value? Measure four paired conditions on the same episode: intact memory, relevant deletion, equally sized irrelevant deletion, and replacement of only the relevant value while holding key/query fixed. Evaluate the replacement against both the old answer and the counterfactual answer.

**Data and controls.** The implemented task has unique keys within each episode and independent random values. Train with eight slots; development evaluation uses sixteen. Compare against exact key lookup as an oracle and chance/shortcut checks. Extension to FIM or a real LLM requires the actual model and protected external benchmark; a toy retrieval result is not that evidence.

**Endpoint and falsifier.** Selective necessity gap (irrelevant-deletion accuracy minus relevant-deletion accuracy), and substitution accuracy as a separate endpoint. A model unaffected by relevant deletion, affected equally by arbitrary deletion, or unable to follow a value-only substitution fails the selective-use hypothesis. Flaw -> deletion is out-of-distribution -> high -> equal-sized deletion and in-support replacement controls -> paired raw logits and labels.

Causal memory selection and tracing already exist [S18,S19]. The present code is an assay implementation, not a claimed novel memory architecture. State: development mechanism and runner implemented, unexecuted. Historical FIM/causal-memory findings remain unchanged.

### 14. Retrieval-Value Memory Eviction (RVME)

**Question and mechanism.** Under a fixed slot/token budget, can estimated marginal answer contribution improve eviction decisions over recency and frequency? Estimate value from training-only paired memory interventions, then evict the item with minimum predicted future loss increase. Estimation overhead counts toward the budget.

**Data and controls.** Long streams with delayed queries, distractors, changing relevance and held-out topic/task generators. Compare FIFO/LRU, reservoir sampling, frequency eviction, relevance retrieval and an offline oracle as a ceiling.

**Endpoint and falsifier.** Answer accuracy and latency at equal memory and total inference budget. If intervention scoring costs more than simply keeping/searching extra items, reject the practical claim. Flaw -> future-query access leaks relevance -> critical -> causal online eviction and future-blind logs -> replayable decision records. Causal memory selection [S18] is close prior work; a new eviction-cost frontier is necessary. This may merge with 13 after novelty review. State: specified, not implemented.

### 15. Counterfactual Replay Without New Data (CRWND)

**Question and mechanism.** Can replaying counterfactual combinations of stored episodes improve transfer without accessing extra external data? Construct replay by altering one known causal variable while preserving valid simulator constraints, then update a model on the resulting task-consistent targets. Ordinary self-generated text is not automatically a valid counterfactual.

**Data and controls.** A simulator with exact counterfactual labels and a separately validated task bank. Split by causal graph and intervention type. Compare ordinary replay, additional training, random recombination and generative replay with equal update counts.

**Endpoint and falsifier.** Transfer performance at equal total training/data-generation cost. Gains disappearing under ordinary replay or accompanied by invalid counterfactual targets fail. Flaw -> synthetic replay creates false rules -> critical -> exact generator checks and intervention support restrictions -> invalid-sample accounting and targeted ablations. Relation to existing counterfactual-world and replay work is unresolved; exhaustive nearest-method review is mandatory. State: specified, not implemented.

### 16. Selective Slow-State Reset (SSSR)

**Question and mechanism.** Can a two-timescale memory system reset obsolete fast context after a mechanism change while preserving task-relevant slow state? The reset gate uses a past-only change statistic, not oracle boundaries. Factorized fast/slow state and explicit reset interventions distinguish the mechanism from simply increasing capacity.

**Data and controls.** Streams with independently changing nuisance and task dynamics, including long stationary controls. Compare no reset, full reset, fixed decay, oracle reset and parameter-matched GRU/state-space models.

**Endpoint and falsifier.** Post-change recovery error plus retained long-term task performance. Failure to outperform a single tuned decay or frequent false resets rejects selective-reset utility. Flaw -> environment labels leak shift boundaries -> critical -> blind gate and negative-control shifts -> logged reset timing and causal interventions. Temporal predictive coding/memory work [S15,S19] provides context but does not establish novelty. State: specified, not implemented.

## E. Scientific operators, experimental design and mathematical structure

### 17. Residual-Certified Krylov Reuse (RCKR)

**Question and mechanism.** Can a cheap residual/spectral diagnostic decide when recycling a subspace is worth its overhead? Before reuse, evaluate the candidate subspace against the new operator and accept only when a predeclared cost/error surrogate predicts benefit. The diagnostic must use fewer operator products than the work it is intended to save.

**Data and controls.** Independent sequences of SPD systems with controlled spectral rotation and condition numbers; later PDE operators with archived provenance. Compare conjugate gradients, standard recycled/deflated CG, a fixed reuse schedule and an oracle schedule.

**Endpoint and falsifier.** Total operator products and wall time to the same residual tolerance, including diagnostic cost. No saving against standard recycling or false certificates under eigenspace rotation fail. Flaw -> residual norm not equal solution error without conditioning -> critical -> state the condition-number bound and include adversarial rotations -> exact small-system verification. Recycling is established [S20,S21]. This is a potential distinct successor to Krylov-JEPA, not a claim its earlier result became positive. State: specified, not implemented.

### 18. Constraint-Aware Operator Coverage (CAOC)

**Question and mechanism.** Can conformal residual sets be intersected with a verified physical constraint without losing their original coverage when the constraint truly holds? Construct a calibrated set C(x), then C'(x)=C(x) intersect K(x). If the true state lies in K(x), the event y in C' is the same as y in C; approximate or wrong constraints invalidate that argument.

**Data and controls.** A manufactured-solution PDE and independently generated trajectories with exact versus approximate conservation. Split by whole trajectory/parameter family. Compare unmodified conformal sets, naive projected means, residual-normalized intervals and current operator-conformal methods.

**Endpoint and falsifier.** Set size at fixed simultaneous/functional coverage, explicitly distinguished from pixelwise coverage. If constraints are uncertain or only pixelwise coverage is achieved for a whole-field claim, the proposed guarantee fails. Flaw -> approximate physics excludes truth -> critical -> tolerance sets with verified discretization error -> exact inclusion checks and misspecification stress tests. Existing operator conformal methods [S22,S23] prevent a generic novelty claim. State: specified, not implemented.

### 19. Misspecification-Aware Theory Discrimination (MATD)

**Question and mechanism.** Can an experiment policy recognize that none of its candidate physical models fits, rather than becoming confidently wrong? Add a model-discrepancy alternative, compare robust information gain with ordinary expected information gain, and measure decision behavior when the true mechanism is absent from the model library.

**Data and controls.** Synthetic ODE libraries with an independently specified omitted-mechanism family, fixed measurement noise and intervention cost. Compare expected information gain, random/space-filling designs, robust Bayesian design and prediction-error heuristics.

**Endpoint and falsifier.** Wrong-model posterior confidence and identification regret at equal experimental budget, with in-library performance as a constraint. A policy that only becomes less confident without improving decisions or detection fails. Flaw -> discrepancy model absorbs every observation -> high -> regularization and calibrated in-library controls -> joint calibration/regret curves. Robust design work [S24,S25] is close prior art. Preserve the finite-library scope of ATG's historical findings. State: specified, not implemented.

### 20. Minimal Causal State Dimension (MCSD)

**Question and mechanism.** What is the smallest learned latent subspace whose transplantation preserves a specified computation across independently trained models? Find a low-rank alignment using development interventions, then test held-out interchange interventions and donors. A low-dimensional predictive probe is not enough.

**Data and controls.** Algorithmic tasks with a known abstract state and independently trained neural implementations. Split tasks, seeds, donors and intervention locations. Compare random subspaces, principal components, full-state interchange and a directly specified symbolic-state ceiling.

**Endpoint and falsifier.** Held-out interchange-intervention accuracy versus retained rank, with specificity to irrelevant variables. Failure outside donor/training seeds, or an equal random subspace, rejects a minimal causal representation claim. Flaw -> decoder reconstructs discarded information from a bypass -> critical -> audit every information path and break side channels -> target-state and negative-control interventions. This preserves the earlier catalogue direction RI-003; it is not invented anew here. Representation intervention literature [S19,S26] is a starting point; dedicated causal-abstraction review remains necessary. State: specified, not implemented.

## F. Astronomy, multilingual access and efficient inference

### 21. Cadence-Equivariant Light-Curve Representations (CELR)

**Question and mechanism.** Can a representation separate an astrophysical signal from the observation schedule, so that resampling the same underlying event changes uncertainty but not its inferred physical identity? Use continuous-time encoding and a consistency objective across physically valid thinning/rebinning operations, while retaining the actual cadence mask.

**Data and controls.** Synthetic transit/event injection into real background light curves only after data rights and catalogue versions are frozen. Split by star and observing campaign, never overlapping windows of one star across train/test. Compare interpolation baselines, a mask-aware encoder and a non-equivariant equal-capacity model.

**Endpoint and falsifier.** Recovery at a fixed false-positive rate under held-out cadence, with period/depth error secondary. Discarding temporal information until all events look alike fails. Flaw -> augmentation removes the event or leaks the star -> critical -> identifiability-aware thinning and star-group splits -> injection recovery and negative controls. Injection/recovery is established [S27,S28]. This is not confirmation of new planets or an automatic update to IRIS-Space. State: specified, not implemented.

### 22. Selection-Aware Astronomical Anomaly Scores (SAAAS)

**Question and mechanism.** Can anomaly ranking account for a measured detection/selection function instead of mistaking well-observed objects for intrinsically rare ones? Estimate recovery probability on separate injections, use it in a calibrated ranking/uncertainty model, and explicitly cap inverse weights when selection probabilities are near zero.

**Data and controls.** Frozen mission/catalogue releases, instrument-quality covariates, and injection experiments disjoint from evaluation stars. Compare raw anomaly score, signal-to-noise ranking, covariate matching and selection-weighted scores.

**Endpoint and falsifier.** Recovery of withheld anomaly classes at fixed follow-up budget and false-alarm rate. Failure after controlling for brightness/cadence, or instability from very small selection probabilities, rejects the benefit. Flaw -> synthetic injections do not cover real anomalies -> critical -> separate simulated recovery from astrophysical confirmation -> blinded expert follow-up and external populations. Selection/recovery studies [S27,S28,S29] are foundational. State: specified, not implemented; no discovery claim or observational follow-up has occurred.

### 23. Language-Conditioned Access Versus Capability (LCAC)

**Question and mechanism.** When a multilingual model fails in one language, is the relevant concept absent or merely inaccessible through that language's computational pathway? Use matched semantic tasks, language/concept donor separation, and activation interchange to test content rescue while holding the output-language requirement fixed.

**Data and controls.** A frozen multilingual task bank, bilingual validation of semantic equivalence, and separate concept, template and language splits. Compare translation-then-answer, same-language donors, wrong-concept donors, norm-matched random patches and full-state patches.

**Endpoint and falsifier.** Content rescue with preserved output language on held-out semantic cases. Rescue only from memorized templates, generic activation amplification or output-language switching defeats the access-path interpretation. Flaw -> translations change the actual question -> critical -> independent semantic review and minimal pairs -> error taxonomy and counterfactual controls. Prior activation-patching evidence already supports language-agnostic concept representations [S26]; a new study needs sharper failure regimes, not the same broad conclusion. State: specified, not implemented; preserves the user's earlier epistemic-blind-spots direction.

### 24. Error-Certified Weight Reconstruction (ECWR)

**Question and mechanism.** Can a weight generator reconstruct only the next needed block while a computable residual bound determines whether to use the reconstruction or retrieve exact weights? Cache decisions depend on an estimated output perturbation bound and actual device-memory pressure, not on a nominal compression ratio alone.

**Data and controls.** Fixed licensed model checkpoints, fixed evaluation tasks and a declared device/runtime matrix. Compare exact resident weights, lazy exact loading, quantization, low-rank compression and hypernetwork reconstruction. Measure reconstruction, transfer, synchronization and cache costs together.

**Endpoint and falsifier.** End-to-end latency and peak resident memory subject to a predefined output-quality tolerance and failure rate. Reconstruction slower than exact transfer, or a certificate that misses adversarial inputs, rejects the efficiency claim. Flaw -> loose layerwise bounds and uncounted host memory -> critical -> instrument full process/device memory and validate bound violations -> exact-output comparisons and worst-case tests. Hypernetworks are established [S16,S17,S30]. This is a proposed Olympus successor boundary, not proof that existing Olympus runs are fast or complete. State: specified, not implemented.

## Literature anchors and exact scope of review

These sources were located/read at abstract or relevant HTML-section level on 20 October 2026. This is a first-pass screen, not a comprehensive systematic review. Publication status must be checked separately before venue-specific claims. Some recent records are preprints. No source is cited as evidence that an R24 method works.

- S01: Peters, Buhlmann and Meinshausen. Causal inference using invariant prediction: identification and confidence intervals. https://arxiv.org/abs/1501.01332
- S02: Banerjee et al. Using Machine Learning to Assess Short Term Causal Dependence and Infer Network Links. https://arxiv.org/abs/1912.02721
- S03: Causal Local States: Scalable Simultaneous Causal Network Inference and Forecasting for Dynamical Systems. https://arxiv.org/html/2608.17452v1
- S04: Gibbs and Candes. Adaptive Conformal Inference Under Distribution Shift. https://arxiv.org/abs/2106.00170
- S05: Lade, J. and Kumar. Bias-Corrected Adaptive Conformal Inference for Multi-Horizon Time Series Forecasting. https://arxiv.org/abs/2604.13253
- S06: Nathe et al. Reservoir Computing with Noise. https://arxiv.org/abs/2303.00585
- S07: Stochastic Reservoir Computers. https://arxiv.org/html/2405.12382v1
- S08: Lin et al. Learning noise-induced transitions by multi-scaling reservoir computing. https://arxiv.org/abs/2309.05413
- S09: PDEBENCH: An Extensive Benchmark for Scientific Machine Learning. https://arxiv.org/abs/2210.07182
- S10: Parish and Duraisamy. Non-Markovian Closure Models for Large Eddy Simulations using the Mori-Zwanzig Formalism. https://arxiv.org/abs/1611.03311
- S11: Gupta et al. Mori-Zwanzig latent space Koopman closure for nonlinear autoencoder. https://arxiv.org/abs/2310.10745
- S12: Malladi et al. Fine-Tuning Language Models with Just Forward Passes. https://arxiv.org/abs/2305.17333
- S13: Baydin et al. Gradients without Backpropagation. https://arxiv.org/abs/2202.08587
- S14: Millidge et al. Predictive Coding: Towards a Future of Deep Learning beyond Backpropagation? https://arxiv.org/abs/2202.09467
- S15: Learning Long-Range Dependencies with Temporal Predictive Coding. https://arxiv.org/html/2602.18131v2
- S16: Ha et al. HyperNetworks. https://arxiv.org/abs/1609.09106
- S17: Chang, Flokas and Lipson. Principled Weight Initialization for Hypernetworks. https://arxiv.org/abs/2312.08399
- S18: Causal Intervention-Based Memory Selection for Long-Term Conversational Agents. https://arxiv.org/html/2605.17641v1
- S19: How Linear Attention Remembers. https://arxiv.org/html/2609.33093v1
- S20: de Roos and Hennig. Krylov Subspace Recycling for Fast Iterative Least-Squares in Machine Learning. https://arxiv.org/abs/1706.00241
- S21: Ehrhardt, Gazzola and Scott. Efficient gradient-based methods for bilevel learning via recycling Krylov subspaces. https://arxiv.org/abs/2412.08264
- S22: Harris et al. Locally Adaptive Conformal Inference for Operator Models. https://arxiv.org/abs/2507.20975
- S23: Conformal Prediction for Neural Operators: Distribution-Free Uncertainty Quantification. https://arxiv.org/html/2606.09923v1
- S24: Abdulsamad et al. Maximin Robust Bayesian Experimental Design. https://arxiv.org/abs/2603.14094
- S25: Robust Experimental Design via Generalised Bayesian Inference. https://arxiv.org/html/2511.07671v2
- S26: Dumas et al. Activation Patching Reveals Language-Agnostic Concept Representations in Transformers. https://arxiv.org/abs/2411.08745
- S27: Measuring Transit Signal Recovery in the Kepler Pipeline I. https://arxiv.org/html/1303.0255v1
- S28: Measuring Transit Signal Recovery in the Kepler Pipeline IV. https://arxiv.org/html/2010.04796v1
- S29: NASA Exoplanet Archive, Data Columns in the Kepler Stellar Table. https://exoplanetarchive.ipac.caltech.edu/docs/API_keplerstellar_columns.html
- S30: Universal Hypernetworks for Arbitrary Models. https://arxiv.org/abs/2604.02215

## Canonical history and next scientific decisions

This version preserves the distinction between a proposed contribution, an implemented mechanism, an executed experiment and a supported claim. The next valid decision for 01/05/09/13 is engineering verification, then a CUDA-only development pilot after hardware/quota access. The next valid decision for the other twenty is nearest-method review and a full executable model/evaluation specification, not a GPU launch. A final paper is blocked on real evidence, not on polishing prose. No paper should contain invented tables, simulated-as-real data, unearned causal language or an assertion of empirical perfection.
