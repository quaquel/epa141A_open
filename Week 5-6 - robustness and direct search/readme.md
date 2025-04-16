# Week 5-6 - Deep Dive into Many Objective optimization

Welcome to Weeks 5-6 of the course. In the upcomming weeks, you will learn more about many objective optimization using evolutionary algorithms. You will learn how to use these techniques, how to check their performance, and the various ways in which these methods can be used to support decision making under deep uncertianty. 

Throughout Weeks 5-6, you will:

1. Learn about **many objective optimization** and replicate results from influential papers on robust decision making. You will apply epsilon-NSGAII to identify Pareto optimal sets of solutions
2. Continue working with the **lake problem** and use it as a basis for directed search for promosing solutions. You will use a slightly different problem setup where you will optimize a decision rule that can be used at each time step to determine how much antropogenic polution to release given the observed pollution in the lake.
3. Gain hands-on experience in using **Many Objective Evolutionary algorithms** with particular attention for checking the convergence of these algorithms and the importance of doing seed analysis when using MOEAs.
4. Learn more about 3 versions of the **Many Objective Robust Decision Making (MORDM)** framework: MORDM, multi-scenario MORDM, and Many Objective Robust Optimization
5. Develop a better understanding of how to design efffective interventions in complex systems considering multiple competing objectives and in the presen of deep uncertainties, enabling you to prioritize efforts to manage uncertainties effectively and make well-informed decisions.

By the end of Weeks 5-6, you will have a solid foundation in many objective optimization, deepening your understanding of using models to design effective interventions. Armed with these skills, you will be better equipped to analyze complex systems and make more informed decisions in the face of uncertainty.

## Suggested order of assignments

8.  MOEA tutorial - an in depth tutorial for how to apply MOEAs with the ema workbench
9.  MORDM - use epsilon-NSGAII to solve the closed loop control version of the lake problem and evaluate the set of Pareto optimal solutions under deep uncertainty to investigate their robusntess
10. multi-scenario MORDM - use epsilon-NSGAII to solve the closed loop control version of the lake problem for several carefully selected  scenarios representing alternative realizations of the deeply uncertain factors. Next, analyze the solutions found across these seperate optimizations to identify the most promising robust solutions
11. MORO - use epsilon-NSGAII to find optimally robust solutions for the closed loop control version of the lake problem