# AgeLens Research Protocol

## Version 1.0 (Draft)

**Document Type:** Research Protocol
**Status:** Draft for Internal Review
**Project:** AgeLens – Reproducible Biological Age Estimation Framework
**Language:** English (Academic)

---

# 1. Introduction

## 1.1 Purpose of this Protocol

This document defines the scientific, methodological, and governance framework that guides the AgeLens project. Rather than serving as a software manual or implementation guide, it establishes the principles under which all research activities, implementation decisions, validation procedures, and documentation efforts shall be conducted.

The protocol is intended to ensure that the development of AgeLens remains transparent, reproducible, evidence-based, and independently auditable throughout its lifecycle. Every subsequent project document—including literature reviews, methodological reports, implementation notes, validation reports, and software artifacts—shall conform to the principles established herein.

This protocol represents the highest-level governing document of the project.

---

## 1.2 Background

Biological aging represents the progressive decline of physiological function and resilience that occurs over the lifespan. Although chronological age is commonly used as a proxy for aging, individuals of the same chronological age frequently exhibit substantial differences in health status, functional capacity, disease susceptibility, and mortality risk.

To better characterize these differences, multiple biological age models have been proposed. Among them, the Levine PhenoAge methodology has become one of the most widely adopted clinical biomarker–based approaches due to its reproducible association with morbidity and all-cause mortality across diverse populations.

While the mathematical formulation of PhenoAge has been published, reproducing the methodology requires numerous implementation decisions involving biomarker selection, laboratory harmonization, preprocessing, software interpretation, and validation. These decisions are distributed across multiple information sources rather than being described within a single reference.

AgeLens is designed to organize, document, and justify these decisions in a systematic and reproducible manner.

---

## 1.3 Project Philosophy

AgeLens is founded on the principle that scientific reproducibility begins before software implementation.

The project therefore prioritizes methodological correctness over implementation speed. No software component shall be considered complete unless the methodological assumptions underlying its implementation have been explicitly documented and supported by appropriate evidence.

Accordingly, the project follows a **Replication Before Innovation** philosophy.

The primary objective of Version 1 is not to develop a new biological age algorithm, but to reproduce the published Levine methodology as faithfully as possible while documenting every methodological decision required during implementation.

Potential methodological improvements, alternative biomarker configurations, machine learning extensions, and exploratory analyses are considered future work and fall outside the primary objective of Version 1 unless explicitly documented otherwise.

---

# 2. Project Objectives

## 2.1 Primary Objective

To develop a transparent, reproducible, and evidence-based implementation of the published Levine PhenoAge methodology using harmonized NHANES data while maintaining complete methodological traceability.

---

## 2.2 Secondary Objectives

The project additionally seeks to:

* establish a reproducible data preparation workflow for NHANES datasets;
* document every methodological decision affecting implementation;
* provide complete traceability between published evidence and implementation choices;
* create reusable documentation for future biological aging research;
* facilitate independent verification of all preprocessing and modeling steps;
* provide a modular foundation for future explainable AI analyses without altering the original methodology.

---

# 3. Research Questions

The following research questions define the scope of the Version 1 protocol.

### RQ1

How can the original Levine PhenoAge methodology be faithfully reproduced using appropriately harmonized NHANES data?

### RQ2

How should NHANES III laboratory variables be harmonized with modern NHANES laboratory variables while preserving methodological consistency?

### RQ3

How is the original Levine methodology represented across the BioAge software implementation and selected high-impact replication studies?

### RQ4

How can methodological transparency and reproducibility be maximized throughout the implementation process?

### RQ5

Which implementation decisions require explicit methodological justification before software development may proceed?

---

# 4. Project Scope

## 4.1 In Scope

Version 1 includes:

* methodological replication of the published Levine PhenoAge framework;
* systematic literature review relevant to methodological replication;
* NHANES variable harmonization;
* documentation of implementation decisions;
* reproducibility-focused preprocessing;
* validation against published methodology;
* explainability support where it does not alter the original model.

---

## 4.2 Out of Scope

Version 1 explicitly excludes:

* development of new biological age algorithms;
* retraining or reparameterization of the original Levine model unless separately documented;
* clinical diagnosis or treatment recommendation;
* deployment as a medical device;
* deep learning approaches;
* multi-omics integration;
* wearable sensor integration;
* personalized clinical decision support.

Any activity outside this scope shall require a protocol amendment before implementation.

# 5. Scientific Principles

The AgeLens project is governed by a set of scientific principles intended to maximize methodological rigor, transparency, and reproducibility. These principles apply to every phase of the project, including literature review, data preparation, implementation, validation, and documentation.

---

## SP-1. Replication Before Innovation

The primary objective of Version 1 is the faithful replication of the published Levine PhenoAge methodology.

No methodological modification shall be introduced unless the original implementation has first been reproduced to the greatest extent possible using available evidence.

Potential methodological improvements shall be documented separately and must not alter the baseline replication without explicit justification.

---

## SP-2. Evidence Before Implementation

Implementation shall never precede methodological justification.

Before any software component is developed, the methodological rationale supporting its implementation shall be identified, documented, and evaluated.

Whenever possible, implementation decisions should be supported by:

* the original methodological publication;
* official NHANES documentation;
* supplementary materials;
* validated software implementations;
* high-quality replication studies.

---

## SP-3. Transparency

Every methodological decision shall be explicitly documented.

No undocumented preprocessing step, variable transformation, or implementation shortcut shall be considered acceptable.

Project documentation should enable an independent researcher to understand not only *what* decision was made, but also *why* it was made.

---

## SP-4. Reproducibility

The project shall be reproducible from publicly available data and publicly available documentation whenever legally and technically possible.

All preprocessing steps, assumptions, software versions, variable mappings, and methodological choices shall be recorded.

---

## SP-5. Traceability

Every important implementation decision shall be traceable to its supporting evidence.

Traceability shall be maintained throughout the entire research lifecycle.

Each decision should reference:

* supporting evidence;
* associated assumptions;
* related evidence gaps (if any);
* implementation artifacts;
* validation results.

---

## SP-6. Proportional Complexity

Methodological complexity shall be introduced only when justified by evidence.

Additional processing steps, statistical corrections, or implementation layers should not be added solely because they appear more sophisticated.

The simplest scientifically defensible solution should be preferred.

---

## SP-7. Version Stability

Research governance documents should remain stable throughout the project.

Major methodological changes require explicit review and protocol revision.

Frequent changes without documented justification should be avoided to preserve reproducibility.

---

# 6. Research Governance

Scientific projects require explicit governance to ensure that evidence, assumptions, decisions, and remaining uncertainties are managed consistently.

AgeLens therefore distinguishes four different categories of methodological information.

These categories represent different states within the project's evidence lifecycle.

---

# 6.1 Evidence

Evidence represents verified information that supports or refutes a methodological claim.

Evidence may originate from:

* original methodological publications;
* official NHANES documentation;
* peer-reviewed replication studies;
* validated software implementations;
* official statistical documentation.

Evidence itself does not constitute a project decision.

Instead, evidence provides the basis upon which decisions may be made.

---

## Evidence Levels

To improve consistency, evidence shall be classified according to its strength.

| Level  | Description                                      |
| ------ | ------------------------------------------------ |
| **E1** | Original methodological publication              |
| **E2** | Official NHANES / CDC documentation              |
| **E3** | Peer-reviewed replication study                  |
| **E4** | Validated software implementation (e.g., BioAge) |
| **E5** | High-quality secondary literature                |

Evidence levels indicate the origin of information rather than absolute certainty.

Multiple evidence levels may support a single methodological decision.

---

# 6.2 Assumptions

An assumption is a temporary working hypothesis adopted when available evidence is insufficient to support a final methodological decision.

Assumptions are permitted only when:

* implementation cannot reasonably continue without a provisional choice; and
* the uncertainty has been explicitly documented.

Every assumption shall:

* receive a unique identifier;
* describe the rationale;
* specify the missing evidence;
* define the conditions under which the assumption will be re-evaluated.

Assumptions are temporary by definition and shall never be treated as established evidence.

---

# 6.3 Decisions

A decision represents an officially adopted methodological choice.

No decision shall be considered final unless supported by documented evidence and reviewed within the project governance process.

Each decision record shall contain:

* Decision ID
* Title
* Description
* Supporting Evidence
* Evidence Level(s)
* Confidence Rating
* Reviewer
* Date
* Related Assumptions
* Related Evidence Gaps
* Status

---

## Confidence Ratings

Methodological confidence shall be recorded separately from evidence level.

| Rating   | Meaning                                                     |
| -------- | ----------------------------------------------------------- |
| High     | Strong supporting evidence with minimal uncertainty         |
| Moderate | Sufficient evidence with acknowledged limitations           |
| Low      | Decision accepted provisionally pending additional evidence |

Confidence ratings facilitate future review without implying that lower-confidence decisions are invalid.

---

# 6.4 Evidence Gaps

An Evidence Gap is a documented methodological question for which available evidence is currently insufficient to support a definitive decision.

Evidence gaps are expected within scientific research and shall be treated as managed uncertainties rather than project failures.

Examples include:

* unresolved NHANES variable mappings;
* conflicting laboratory documentation;
* inconsistent methodological descriptions across publications;
* unavailable supplementary information.

Documenting an evidence gap is mandatory whenever uncertainty materially affects methodological interpretation.

---

# 6.5 Evidence Lifecycle

Methodological information progresses through the following lifecycle:

Research Question

↓

Evidence Collection

↓

Evidence Appraisal

↓

Evidence Level Assignment

↓

**If sufficient evidence exists**

↓

Decision

↓

Implementation

↓

Validation

↓

Documentation

---

When evidence is insufficient:

Research Question

↓

Evidence Collection

↓

Insufficient Evidence

↓

Assumption

↓

Additional Investigation

↓

Either:

* Decision (if evidence becomes sufficient)

or

* Evidence Gap (if uncertainty remains)

---

# 6.6 Evidence Resolution Policy

Every documented Evidence Gap shall be reviewed before each major project release.

The outcome of the review shall follow one of the following paths, integrating the classification of Core and Peripheral gaps:

| Evidence Resolution | Classification | Required Action |
| :--- | :--- | :--- |
| Resolved | — | Convert to Decision |
| Minor impact | Peripheral | Record as Project Limitation |
| Optional feature affected | Peripheral | Defer to Future Release |
| Core methodology affected | Core | Block implementation until resolved |

Under no circumstances shall unresolved core methodological uncertainties be silently ignored.

## Evidence Gap Escalation

Evidence Gaps shall undergo periodic review.

If an Evidence Gap remains unresolved beyond a planned review milestone, one of the following actions shall be taken:

- document the limitation for the current release;
- remove the affected optional feature;
- postpone release if core methodology is affected.

No unresolved Core Evidence Gap shall remain undocumented at release.

---

# 6.7 Decision Review Policy

Scientific knowledge evolves over time.

Therefore, methodological decisions are considered reviewable rather than immutable.

A decision shall be re-evaluated when:

* new primary evidence becomes available;
* official NHANES documentation changes;
* methodological errors are identified;
* reproducibility cannot be independently confirmed.

Every revision shall preserve the complete historical record of previous decisions.

No decision shall be overwritten without documentation of the reason for change.

# 7. Research Quality System

## 7.1 Purpose

Scientific quality within the AgeLens project is not measured solely by implementation correctness. Instead, quality is defined as the degree to which every methodological decision is scientifically justified, reproducible, transparent, traceable, and independently auditable.

The purpose of the Research Quality System (RQS) is to establish a standardized framework for evaluating the scientific integrity of every project artifact before implementation and release.

The RQS applies to:

- literature reviews;
- methodological reports;
- NHANES harmonization;
- implementation decisions;
- validation procedures;
- software releases;
- project documentation.

Quality assurance is therefore considered an integral component of the research process rather than a final verification step.

---

## 7.2 Quality Objectives

The Research Quality System shall ensure that:

1. every methodological decision is evidence-based;
2. assumptions are explicitly documented;
3. unresolved uncertainties remain visible;
4. documentation is internally consistent;
5. implementation is reproducible;
6. independent reviewers can reconstruct the decision-making process.

---

## 7.3 Quality Requirements

Before any methodological decision becomes active, the following requirements shall be evaluated.

### Q1 — Research Question

Is the underlying research question clearly defined?

---

### Q2 — Evidence Availability

Has all currently available evidence been collected?

---

### Q3 — Evidence Classification

Has the supporting evidence been classified according to the project's Evidence Level taxonomy?

---

### Q4 — Evidence Consistency

Have conflicting publications or documentation sources been evaluated?

---

### Q5 — Assumption Assessment

Have all temporary assumptions been explicitly documented?

---

### Q6 — Evidence Gap Assessment

Does any unresolved Evidence Gap remain?

If yes, has it been categorized according to the Evidence Resolution Policy?

---

### Q7 — Reproducibility

Can another researcher independently reproduce the reasoning process?

---

### Q8 — Traceability

Can every implementation decision be traced back to supporting evidence?

---

## 7.4 Evidence Sufficiency

Evidence shall be considered sufficient when at least one of the following conditions is satisfied:

### Category A

A primary methodological publication directly supports the decision.

---

### Category B

Official NHANES or CDC documentation confirms the implementation.

---

### Category C

A validated software implementation reproduces the published methodology and is consistent with primary literature.

---

### Category D

Only one high-quality source exists.

In such cases the decision may proceed only if:

- the limitation is explicitly documented;
- an Assumption has been registered;
- the decision is marked with Moderate or Low confidence;
- the issue is scheduled for future review.

A Category D Decision is considered provisional.

During subsequent reviews, additional evidence shall be actively sought.

If sufficient supporting evidence is identified, the Decision shall be upgraded accordingly.

If the Decision cannot be adequately strengthened after review, it shall be reclassified as an Evidence Gap in accordance with Section 6.6.

Category D Decisions shall not remain indefinitely in a low-confidence state.

---

## 7.5 Core and Peripheral Evidence Gaps

Not all unresolved uncertainties have the same impact. Evidence Gaps shall therefore be classified into two categories, which determine their resolution path as defined in Section 6.6.

### Core Evidence Gaps

Core gaps directly affect:

- biomarker definitions;
- model equations;
- preprocessing;
- NHANES harmonization;
- mortality calculations;
- statistical validity.

### Peripheral Evidence Gaps

Peripheral gaps affect:

- documentation wording;
- optional analyses;
- visualization;
- supplementary examples;
- implementation convenience.

---

## 7.6 Release Readiness

Version 1 shall not be released unless the following conditions have been satisfied.

| Requirement | Status |
|-------------|--------|
| Protocol finalized | Required |
| Literature review completed | Required |
| Evidence Matrix completed | Required |
| Decision Log reviewed | Required |
| Evidence Gap review completed | Required |
| NHANES Harmonization reviewed | Required |
| Validation completed | Required |
| Documentation synchronized | Required |

Failure to satisfy any mandatory requirement postpones release.

---

## 7.7 Independent Review

Major project milestones shall undergo an independent methodological review.

Reviewers should evaluate:

- scientific consistency;
- evidence quality;
- documentation completeness;
- reproducibility;
- traceability;
- remaining uncertainties.

Review comments shall be preserved as part of the project record.

---

## 7.8 Continuous Improvement

The Research Quality System shall evolve through documented revisions.

Quality improvements shall be based upon:

- new scientific evidence;
- reviewer feedback;
- implementation experience;
- updated NHANES documentation;
- reproducibility findings.

Changes to the Quality System require protocol revision and version tracking.

# 8. Documentation Architecture

## 8.1 Purpose

High-quality research depends not only on methodological rigor but also on consistent, transparent, and maintainable documentation.

The purpose of the Documentation Architecture is to establish a unified documentation standard that enables every research artifact produced within the AgeLens project to be understandable, reproducible, traceable, and independently reviewable.

All project documents shall conform to the standards defined in this section.

---

## 8.2 Documentation Principles

The documentation system is governed by the following principles.

### DP-1. Single Source of Truth

Each methodological concept shall have one authoritative document.

Information shall not be duplicated across multiple documents unless required for contextual explanation.

When duplication is unavoidable, one document shall be designated as the primary source.

---

### DP-2. Traceability

Every document shall reference the evidence, decisions, assumptions, and related documents upon which it depends.

Readers should be able to navigate from a conclusion back to the supporting evidence without ambiguity.

---

### DP-3. Consistency

Terminology, abbreviations, identifiers, and methodological definitions shall remain consistent across all project documentation.

Changes to terminology require coordinated updates throughout the documentation system.

---

### DP-4. Modularity

Each document shall address a single well-defined purpose.

Large topics should be divided into smaller, interconnected documents rather than consolidated into a single monolithic report.

---

### DP-5. Version Awareness

Every document shall include version information and revision history.

Historical versions shall remain accessible for reproducibility purposes.

---

# 8.3 Documentation Hierarchy

Project documentation is organized into the following categories.

| Category                     | Purpose                               |
| ---------------------------- | ------------------------------------- |
| Research Protocol            | Governing principles                  |
| Literature Reviews           | Analysis of scientific publications   |
| Methodology Reports          | Technical implementation guidance     |
| Governance Records           | Decisions, assumptions, evidence gaps |
| Validation Reports           | Verification activities               |
| Implementation Documentation | Software-specific documentation       |
| Release Documentation        | Public release information            |

Each category serves a distinct role and shall avoid unnecessary overlap.

---

# 8.4 Standard Document Structure

Unless justified otherwise, every major project document should contain the following sections:

1. Purpose
2. Scope
3. Background
4. Methodology
5. Results or Findings
6. Discussion
7. Limitations
8. Decisions
9. References
10. Revision History

Not all sections are mandatory for every document; however, omissions should be justified.

---

# 8.5 Metadata Requirements

Every document shall include the following metadata.

| Field             | Description                          |
| ----------------- | ------------------------------------ |
| Document Title    | Official document title              |
| Version           | Semantic version number              |
| Status            | Draft / Review / Approved / Archived |
| Author            | Document owner                       |
| Reviewer          | Reviewer(s), if applicable           |
| Last Updated      | Date of latest revision              |
| Related Documents | Cross-referenced documents           |

Metadata supports traceability and document management.

---

# 8.6 Document Naming Convention

To promote consistency, document names shall follow standardized naming conventions.

Examples include:

* `00_Research_Protocol.md`
* `Paper_001_Levine2018.md`
* `Paper_002_BioAge.md`
* `NHANES_Harmonization_Report.md`
* `Decision_Log.md`
* `Evidence_Gap_Register.md`
* `Assumption_Register.md`
* `Validation_Report.md`
* `Variable_Mapping_Table.md`

Names should be descriptive, stable, and avoid unnecessary abbreviations.

---

# 8.7 Cross-Reference Policy

Documents shall explicitly reference related project artifacts whenever methodological dependencies exist.

Examples include:

* Literature reviews referencing supporting Evidence IDs.
* Methodology reports referencing Decision IDs.
* Validation reports referencing implementation versions.
* Decision records referencing supporting publications.
* Evidence Gap records referencing affected project components.

Cross-references shall use persistent identifiers whenever possible.

---

# 8.8 Document Lifecycle

Every project document progresses through the following lifecycle:

Draft

↓

Internal Review

↓

Revision

↓

Approved

↓

Published (Internal)

↓

Archived (if superseded)

Archived documents shall remain available for historical reference and reproducibility.

---

# 8.9 Review and Approval

Major project documents shall undergo structured review before approval.

The review process should evaluate:

* scientific accuracy;
* internal consistency;
* completeness;
* traceability;
* clarity;
* compliance with this protocol.

Approval signifies that the document satisfies the methodological and documentation standards of the project.

---

# 8.10 Documentation Quality Metrics

Documentation quality shall be assessed using the following criteria.

| Criterion       | Objective                     |
| --------------- | ----------------------------- |
| Completeness    | Required sections are present |
| Consistency     | Terminology is uniform        |
| Traceability    | Evidence can be followed      |
| Reproducibility | Methods can be replicated     |
| Readability     | Scientific writing is clear   |
| Maintainability | Future updates are manageable |

These metrics provide a structured basis for evaluating documentation quality during project reviews.

---

# 8.11 Relationship Between Documents

The following hierarchy illustrates how major project documents interact.

Research Protocol

↓

Literature Reviews

↓

Methodology Reports

↓

Governance Records

↓

Implementation

↓

Validation Reports

↓

Release Documentation

This hierarchy ensures that implementation is always grounded in documented evidence and approved methodological decisions.

---

# 8.12 Documentation Philosophy

Documentation within AgeLens is not considered a by-product of implementation.

Instead, documentation is treated as a first-class scientific artifact that records the reasoning process underlying every methodological decision.

Accordingly, documentation shall evolve alongside implementation rather than after implementation has been completed.

# 9. Literature Review Methodology

## 9.1 Purpose

The purpose of the literature review is not merely to summarize existing publications, but to establish a robust methodological evidence base for every scientific decision made throughout the AgeLens project.

Accordingly, literature review within AgeLens is considered an evidence-generation activity rather than a descriptive academic exercise.

Every methodological decision adopted during implementation shall be traceable to documented evidence obtained through the literature review process.

---

# 9.2 Objectives

The literature review has five primary objectives.

1. Identify the original methodological foundations of the Levine PhenoAge framework.

2. Evaluate subsequent methodological replications and validation studies.

3. Identify implementation differences across software packages and published studies.

4. Document methodological uncertainties requiring further investigation.

5. Generate evidence supporting implementation decisions.

---

# 9.3 Review Strategy

The review shall be conducted incrementally.

Rather than attempting a single comprehensive review, literature shall be evaluated paper by paper.

Each publication shall receive an independent technical review before its findings are incorporated into project governance.

This approach improves transparency, traceability, and reproducibility.

---

# 9.4 Search Sources

Priority shall be given to peer-reviewed scientific sources.

Preferred databases include:

* PubMed
* Google Scholar
* Web of Science
* Scopus

When necessary, additional evidence may be obtained from:

* CDC documentation
* NHANES documentation
* Official software repositories
* Supplementary materials
* Author documentation

Grey literature may be consulted only when no peer-reviewed alternative exists.

---

# 9.5 Inclusion Criteria

Publications should satisfy one or more of the following criteria.

* Original methodological publication.

* Peer-reviewed validation study.

* Large-scale epidemiological application.

* Official software implementation.

* NHANES methodological documentation.

* Statistical methodology relevant to implementation.

---

# 9.6 Exclusion Criteria

The following publications shall normally be excluded.

* Editorials.

* Opinion articles.

* Conference abstracts lacking methodological detail.

* Publications without sufficient implementation information.

* Duplicate analyses.

* Studies unrelated to biological age estimation.

Exclusions shall be documented whenever uncertainty exists.

---

# 9.7 Literature Classification

Each publication shall be assigned one primary category.

| Category             | Description                        |
| -------------------- | ---------------------------------- |
| Original Methodology | Foundational methodological papers |
| Replication          | Reproduction of published methods  |
| Validation           | External validation studies        |
| Application          | Clinical or epidemiological use    |
| Software             | Computational implementation       |
| NHANES               | Dataset-specific methodology       |
| Statistical          | Supporting statistical methods     |

A publication may contribute evidence to multiple research questions while retaining one primary classification.

---

# 9.8 Evidence Extraction

For every reviewed publication, the following information shall be extracted.

* Research objective.
* Population.
* Dataset.
* Biomarkers.
* Mathematical methodology.
* Statistical procedures.
* Software implementation.
* Validation strategy.
* Limitations.
* Methodological assumptions.
* Remaining uncertainties.
* Relevance to AgeLens.

Evidence extraction shall prioritize methodological information over narrative discussion.

---

# 9.9 Critical Appraisal

Each publication shall undergo structured methodological appraisal.

Evaluation criteria include:

* methodological clarity;
* reproducibility;
* transparency;
* statistical validity;
* implementation detail;
* consistency with original methodology.

Appraisal focuses on methodological reliability rather than publication prestige.

---

# 9.10 Literature Matrix

Every reviewed publication shall be recorded in the Literature Matrix.

The matrix shall include:

* Paper ID
* Citation
* Category
* Dataset
* Biomarkers
* NHANES usage
* Software availability
* Validation status
* Evidence Level
* Related Research Questions
* Related Decisions
* Notes

The Literature Matrix serves as the project's master index of scientific publications.

---

# 9.11 Paper Review Workflow

### Orientation Reading

Orientation reading is intended solely to improve researcher familiarity with a topic.

No governance artifact is required.

Orientation reading shall not directly influence methodological decisions.

---

### Formal Literature Review

Only publications intended to support methodological decisions shall enter the formal review workflow.

Each formally reviewed paper shall follow the standardized workflow below.

Paper Selection

↓

Initial Reading

↓

Technical Reading

↓

Evidence Extraction

↓

Critical Appraisal

↓

Paper Review Document

↓

Evidence Matrix

↓

Decision Support

↓

Project Documentation

No publication shall directly influence implementation without first completing this workflow.

---

# 9.12 Handling Conflicting Evidence

Scientific disagreement is expected.

When multiple publications present conflicting methodological recommendations:

1. the disagreement shall be documented;

2. supporting evidence shall be evaluated according to Evidence Levels;

3. methodological differences shall be summarized;

4. the rationale for the selected implementation shall be explicitly documented;

5. unresolved disagreements shall be registered as Evidence Gaps when necessary.

Conflicting evidence shall never be ignored.

---

# 9.13 Relationship with Governance

The literature review supports, but does not replace, project governance.

Evidence obtained through literature review may lead to:

* new Decisions;
* revised Decisions;
* new Assumptions;
* closure of existing Evidence Gaps;
* creation of new Research Questions.

Scientific publications therefore function as dynamic inputs to the governance process.

---

# 9.14 Deliverables

The literature review process produces the following project artifacts.

* Paper Review Documents
* Literature Matrix
* Evidence Matrix
* Decision Log updates
* Evidence Gap updates
* Methodology recommendations

Each deliverable contributes to maintaining complete methodological traceability throughout the project.

---

# 9.15 Guiding Principle

The objective of literature review within AgeLens is not to maximize the number of reviewed publications.

Instead, the objective is to maximize the scientific reliability of every methodological decision.

Accordingly, quality shall always take precedence over quantity.

# 10. NHANES Governance and Harmonization Policy

## 10.1 Purpose

The purpose of this section is to define the governance principles governing the use of NHANES data throughout the AgeLens project.

This protocol does not specify the technical implementation of NHANES harmonization. Instead, it establishes the decision-making framework that shall guide all harmonization activities.

Technical details shall be documented separately within the NHANES Harmonization Report.

---

# 10.2 Guiding Principles

NHANES harmonization shall adhere to the following principles.

### HG-1. Methodological Fidelity

Variable harmonization shall preserve the scientific intent of the original Levine methodology whenever possible.

Whenever harmonization requires methodological interpretation, the rationale shall be explicitly documented.

---

### HG-2. Evidence-Based Harmonization

Variable mappings shall never rely solely on software implementation or community practice.

Every mapping shall be supported by one or more of the following:

* original methodological publications;
* official NHANES documentation;
* CDC laboratory documentation;
* validated replication studies.

---

### HG-3. Documentation Before Transformation

No variable transformation shall be implemented before its methodological rationale has been documented.

Documentation shall precede implementation.

---

### HG-4. Reproducibility

Every harmonization decision shall be reproducible by an independent researcher using publicly available documentation.

---

# 10.3 Variable Mapping Policy

Each harmonized variable shall possess a documented mapping record.

The mapping record shall include:

* Variable ID
* NHANES cycle(s)
* Original variable name(s)
* Harmonized variable name
* measurement units
* Laboratory method
* Supporting documentation
* Decision ID
* Confidence rating
* Notes

No harmonized variable shall exist without a corresponding mapping record.

---

# 10.4 Laboratory Method Compatibility

Changes in laboratory methodology across NHANES cycles may affect comparability.

Accordingly, every biomarker shall undergo laboratory compatibility assessment before inclusion.

Assessment shall consider:

* analytical method;
* assay generation;
* calibration procedures;
* reference ranges;
* documented CDC recommendations.

Whenever laboratory equivalence cannot be established, the issue shall be documented as an Evidence Gap until resolved.

---

# 10.5 Unit Standardization

All laboratory measurements shall be evaluated for consistency of measurement units.

Unit conversion shall occur only when scientifically justified.

Every conversion shall include:

* original unit;
* converted unit;
* conversion formula;
* supporting reference;
* validation procedure.

Unit conversions shall be fully reproducible.

---

# 10.6 Missing Biomarkers

Some NHANES cycles may not contain every biomarker required for methodological replication.

Missing biomarkers shall be managed according to the following hierarchy.

### Category A

Temporary absence due to documentation uncertainty.

Action:

Register an Assumption and continue investigation.

---

### Category B

Biomarker unavailable within a specific survey cycle.

Action:

Evaluate alternative NHANES survey cycles.

Document the evaluation within the NHANES Harmonization Report.

Record the final inclusion or exclusion decision in the Decision Log.

Update the Variable Mapping Table accordingly.

If no scientifically defensible alternative exists, formally exclude the affected survey cycle and document the rationale.

---

### Category C

Biomarker unavailable for Version 1 implementation.

Action:

Register an Evidence Gap.

Determine whether the missing biomarker affects core methodology.

If core methodology is compromised, implementation shall not proceed until a justified resolution has been documented.

---

# 10.7 Conflicting Documentation

Conflicts may arise between:

* original publications;
* NHANES documentation;
* CDC documentation;
* software implementations;
* replication studies.

Conflicts shall never be resolved through undocumented judgment.

Instead, the following process shall be applied.

1. Identify all conflicting sources.

2. Classify supporting evidence according to Evidence Levels.

3. Document methodological differences.

4. Evaluate scientific implications.

5. Record the final decision within the Decision Log.

6. Register remaining uncertainty as an Evidence Gap when appropriate.

---

# 10.8 Harmonization Review

Before implementation, every harmonized variable shall undergo review.

The review shall evaluate:

* variable identity;
* measurement consistency;
* laboratory compatibility;
* methodological appropriateness;
* documentation completeness;
* traceability.

Variables failing review shall not enter the implementation pipeline.

---

# 10.9 NHANES Version Compatibility

Different NHANES cycles may contain:

* renamed variables;
* modified laboratory methods;
* revised documentation;
* updated coding systems.

Version compatibility shall therefore be evaluated explicitly rather than assumed.

Compatibility assessments shall be documented within the NHANES Harmonization Report.

---

# 10.10 Deliverables

Implementation of this policy shall produce the following project artifacts.

* NHANES Harmonization Report
* Variable Mapping Table
* Laboratory Compatibility Matrix
* Unit Conversion Register
* Harmonization Decision Log
* Evidence Gap Updates

These artifacts collectively ensure that every harmonization decision remains scientifically justified, reproducible, and independently auditable.

---

# 10.11 Guiding Principle

The objective of NHANES harmonization is not to maximize dataset compatibility.

Instead, the objective is to preserve methodological validity while maintaining complete transparency regarding every harmonization decision.

Whenever methodological fidelity and implementation convenience conflict, methodological fidelity shall take precedence.

# 11. Project Governance, Release Management, and Lifecycle

## 11.1 Purpose

The purpose of this section is to define how the AgeLens project is governed throughout its lifecycle.

Research governance extends beyond methodological decisions and includes project planning, review procedures, release management, document control, and long-term maintenance.

The objective is to ensure that the project remains scientifically reliable while allowing controlled evolution over time.

---

# 11.2 Project Lifecycle

The AgeLens project follows a staged research lifecycle.

Each stage must satisfy predefined quality criteria before progression to the next stage.

Research Questions
↓
Literature Review
↓
Evidence Collection
↓
Governance Review
↓
Methodology Development
↓
Implementation
↓
Validation
↓
Documentation Review
↓
Release
↓
Maintenance

No stage shall be bypassed without documented justification.

---

# 11.3 Deliverables

Each project phase produces one or more formal deliverables.

| Phase              | Primary Deliverables                                     |
| ------------------ | -------------------------------------------------------- |
| Governance         | Research Protocol                                        |
| Literature         | Paper Reviews, Literature Matrix                         |
| Evidence           | Evidence Matrix                                          |
| Harmonization      | NHANES Harmonization Report                              |
| Methodology        | Replication Protocol, Validation Protocol                |
| Governance Records | Decision Log, Assumption Register, Evidence Gap Register |
| Implementation     | Source Code, Pipelines                                   |
| Validation         | Validation Reports                                       |
| Release            | Release Notes, Changelog                                 |

Each deliverable shall be version controlled and traceable.

---

# 11.4 Versioning Policy

The project shall follow Semantic Versioning principles for governance documents.

### Major Version (vX.0)

Represents substantial methodological or governance changes that may affect reproducibility.

Examples include:

* protocol restructuring;
* revised evidence taxonomy;
* changes to methodological principles.

---

### Minor Version (v1.X)

Represents additions or clarifications that do not alter established methodology.

Examples include:

* additional references;
* documentation improvements;
* expanded explanations.

---

### Patch Version (v1.0.X)

Represents editorial corrections.

Examples include:

* spelling corrections;
* formatting improvements;
* broken cross-reference fixes.

Patch releases shall not modify scientific conclusions.

---

# 11.5 Release Governance

A project release shall occur only after successful completion of the required review process.

Each release shall include:

* updated documentation;
* reviewed Decision Log;
* reviewed Evidence Gap Register;
* validated implementation;
* synchronized version history;
* release notes summarizing changes.

Every release shall be reproducible from the associated project version.

---

# 11.6 Protocol Freeze Policy

The Research Protocol is intended to remain stable throughout the project.

Following approval of Version 1.0, the protocol enters **Protocol Freeze** status.

During Protocol Freeze:

* editorial corrections remain permitted;
* reference updates remain permitted;
* clarification of existing content remains permitted.

However, methodological changes require:

1. documented justification;
2. review;
3. protocol amendment;
4. new version number.

Protocol stability is considered essential for long-term reproducibility.

---

# 11.7 Change Control

Every significant project change shall be evaluated before implementation.

Change requests shall include:

* description of the proposed change;
* rationale;
* affected documents;
* affected decisions;
* potential risks;
* expected scientific impact.

Approved changes shall be documented within the revision history.

---

# 11.8 Project Review

Formal project reviews shall be conducted at major milestones.

Review objectives include:

* scientific consistency;
* methodological completeness;
* documentation quality;
* implementation progress;
* validation status;
* remaining evidence gaps.

Review findings shall be preserved as part of the permanent project record.

---

# 11.9 Long-Term Maintenance

Scientific knowledge evolves continuously.

Accordingly, AgeLens shall be maintained through periodic evidence review.

Maintenance activities include:

* monitoring new methodological publications;
* reviewing updated NHANES documentation;
* evaluating software dependency changes;
* assessing reproducibility findings from independent users.

Maintenance updates shall preserve compatibility with previous project versions whenever possible.

---

# 11.10 Success Criteria

Version 1 shall be considered scientifically complete when:

* the original Levine methodology has been faithfully replicated;
* NHANES harmonization has been fully documented;
* all core methodological decisions are supported by documented evidence;
* unresolved core Evidence Gaps have been addressed;
* implementation has been independently reproducible;
* documentation is internally consistent and traceable.

Scientific completeness does not imply that future improvements are unnecessary; rather, it indicates that Version 1 satisfies its predefined research objectives.

---

# 11.11 Project Philosophy

AgeLens is not intended to maximize implementation speed or software complexity.

Instead, the project seeks to maximize scientific reliability.

Throughout the project lifecycle, methodological correctness shall always take precedence over implementation convenience.

Research quality, transparency, and reproducibility remain the primary measures of project success.

# 12. Appendices

The appendices provide standardized templates, controlled vocabularies, and reference structures used throughout the AgeLens project.

These appendices are considered normative components of this protocol unless explicitly stated otherwise.

---

# Appendix A — Glossary

| Term              | Definition                                                                                                       |
| ----------------- | ---------------------------------------------------------------------------------------------------------------- |
| Biological Age    | An estimate of physiological aging based on biological measurements rather than chronological age.               |
| Chronological Age | Age measured from date of birth.                                                                                 |
| Evidence          | Verified information supporting or refuting a methodological claim.                                              |
| Evidence Gap      | A documented unresolved methodological uncertainty.                                                              |
| Assumption        | A temporary working hypothesis pending additional evidence.                                                      |
| Decision          | An officially adopted methodological choice.                                                                     |
| Harmonization     | The process of ensuring methodological comparability across NHANES survey cycles.                                |
| Replication       | Faithful reproduction of a published scientific methodology.                                                     |
| Traceability      | Ability to connect implementation decisions back to their supporting evidence.                                   |
| Reproducibility   | Ability of an independent researcher to obtain equivalent methodological results using the documented procedure. |

---

# Appendix B — Acronyms

| Acronym | Meaning                                          |
| ------- | ------------------------------------------------ |
| BA      | Biological Age                                   |
| CA      | Chronological Age                                |
| CDC     | Centers for Disease Control and Prevention       |
| NHANES  | National Health and Nutrition Examination Survey |
| RQ      | Research Question                                |
| QA      | Quality Assurance                                |
| RQS     | Research Quality System                          |
| SOP     | Standard Operating Procedure                     |
| EG      | Evidence Gap                                     |
| ID      | Identifier                                       |

---

# Appendix C — Evidence Level Summary

| Level | Description                         | Typical Source                      |
| ----- | ----------------------------------- | ----------------------------------- |
| E1    | Original methodological publication | Peer-reviewed article               |
| E2    | Official technical documentation    | CDC / NHANES documentation          |
| E3    | Peer-reviewed replication           | Validation studies                  |
| E4    | Validated implementation            | Official software package           |
| E5    | Secondary scientific literature     | Reviews, methodological discussions |

Evidence Levels indicate the origin of supporting evidence and shall not be interpreted as an absolute measure of scientific certainty.

---

# Appendix D — Decision Record Template

Every methodological decision shall be documented using the following structure.

| Field                     | Description                   |
| ------------------------- | ----------------------------- |
| Decision ID               | Unique identifier             |
| Title                     | Short descriptive title       |
| Description               | Detailed explanation          |
| Related Research Question | Applicable RQ(s)              |
| Supporting Evidence       | Evidence identifiers          |
| Evidence Level            | E1–E5                         |
| Confidence Rating         | High / Moderate / Low         |
| Reviewer                  | Responsible reviewer          |
| Status                    | Draft / Approved / Superseded |
| Date                      | Decision date                 |
| Related Assumptions       | Associated assumptions        |
| Related Evidence Gaps     | Associated evidence gaps      |

---

# Appendix E — Assumption Template

Each assumption shall include:

* Assumption ID
* Description
* Justification
* Missing Evidence
* Expected Resolution
* Related Decision
* Review Date
* Status

Assumptions remain provisional until either converted into Decisions or reclassified as Evidence Gaps.

---

# Appendix F — Evidence Gap Template

Each Evidence Gap shall include:

* Evidence Gap ID
* Description
* Affected Component
* Scientific Impact
* Classification (Core / Peripheral)
* Existing Evidence
* Missing Evidence
* Planned Resolution
* Review Status

Every Evidence Gap shall be reviewed before each major project release.

---

# Appendix G — Paper Review Template

Each reviewed publication shall include:

1. Citation
2. Research Objective
3. Dataset
4. Population
5. Biomarkers
6. Statistical Methodology
7. Software
8. Validation Strategy
9. Strengths
10. Limitations
11. Methodological Decisions
12. Relevance to AgeLens
13. Evidence Level
14. Notes

This template standardizes all literature reviews conducted within the project.

---

# Appendix H — Review Form

Formal project reviews should document:

* Reviewer
* Date
* Reviewed Artifact
* Review Scope
* Major Findings
* Minor Findings
* Recommendations
* Required Actions
* Review Outcome

Possible outcomes include:

* Approved
* Approved with Minor Revisions
* Major Revision Required
* Rejected

---

# Appendix I — Change Request Form

Every significant methodological modification shall include:

* Change Request ID
* Description
* Scientific Justification
* Supporting Evidence
* Expected Impact
* Affected Documents
* Risk Assessment
* Reviewer
* Approval Status
* Implementation Date

Approved changes shall be reflected in the project revision history.

---

# Appendix J — Traceability Matrix (Conceptual)

The project maintains complete methodological traceability.

The conceptual workflow is illustrated below.

Research Question

↓

Evidence

↓

Decision

↓

Implementation

↓

Validation

↓

Documentation

↓

Release

Every implementation artifact should be traceable back to one or more documented research questions and supporting evidence.

---

# Appendix K — Project Documentation Inventory

The following core documents constitute the AgeLens documentation system.

| Document                    | Purpose                      |
| --------------------------- | ---------------------------- |
| Research Protocol           | Governance framework         |
| Literature Matrix           | Publication index            |
| Evidence Matrix             | Evidence tracking            |
| Decision Log                | Methodological decisions     |
| Assumption Register         | Temporary assumptions        |
| Evidence Gap Register       | Outstanding uncertainties    |
| NHANES Harmonization Report | Variable harmonization       |
| Replication Protocol        | Implementation methodology   |
| Validation Protocol         | Validation procedures        |
| Release Notes               | Public release documentation |
| Variable Mapping Table      | Defines cross-cycle variable mappings, laboratory methods, unit harmonization, Decision IDs, and confidence ratings for every harmonized NHANES variable. |

This inventory shall be updated as new project artifacts are introduced.

---

# Closing Statement

This protocol establishes the scientific governance framework for the AgeLens project.

Its purpose is not merely to document procedures, but to ensure that every methodological decision remains transparent, reproducible, evidence-based, and independently auditable.

Future project documents, software implementations, validation studies, and scientific publications shall conform to the principles defined within this protocol.

The protocol shall remain the authoritative reference governing methodological conduct throughout the lifecycle of the AgeLens project.

# Front Matter

## Document Control

| Field           | Value                                              |
| --------------- | -------------------------------------------------- |
| Document Title  | AgeLens Research Governance & Methodology Protocol |
| Project         | AgeLens                                            |
| Document ID     | AL-RP-001                                          |
| Version         | 1.0 (Draft)                                        |
| Status          | Internal Review                                    |
| Language        | English                                            |
| Owner           | AgeLens Research Project                           |
| Classification  | Internal Research Documentation                    |
| Approval Status | Pending                                            |
| Effective Date  | To be assigned upon approval                       |

---

## Revision History

| Version | Date       | Author       | Summary of Changes                             |
| ------- | ---------- | ------------ | ---------------------------------------------- |
| 0.1     | YYYY-MM-DD | Project Team | Initial protocol draft                         |
| 0.5     | YYYY-MM-DD | Project Team | Governance framework established               |
| 0.8     | YYYY-MM-DD | Project Team | Documentation architecture completed           |
| 0.9     | YYYY-MM-DD | Project Team | NHANES governance and quality system completed |
| 1.0     | YYYY-MM-DD | Project Team | First approved protocol                        |

Future revisions shall preserve this history to ensure full document traceability.

---

## Document Approval

| Role                    | Name | Signature | Date |
| ----------------------- | ---- | --------- | ---- |
| Principal Researcher    |      |           |      |
| Methodological Reviewer |      |           |      |
| Scientific Reviewer     |      |           |      |

Approval indicates that the document has successfully completed the project's review process.

---

## Distribution

This protocol governs all methodological activities within the AgeLens project.

Controlled copies may be distributed internally.

Public versions may omit administrative information while preserving methodological content.

---

## Reading Guide

New contributors should read project documentation in the following order:

1. Research Protocol
2. Literature Review Documents
3. NHANES Harmonization Report
4. Decision Log
5. Evidence Matrix
6. Replication Protocol
7. Validation Protocol
8. Implementation Documentation

Following this sequence ensures that implementation is understood within its methodological context.

---

## Relationship to Other Documents

This protocol serves as the highest-level governance document.

The hierarchy is:

Research Protocol

↓

Methodology Reports

↓

Governance Records

↓

Implementation Documentation

↓

Validation Reports

↓

Release Documentation

Lower-level documents shall not contradict the principles established within this protocol.

# References

## Core Methodology

Klemera, P., & Doubal, S. (2006). A new approach to the concept and computation of biological age. *Mechanisms of Ageing and Development, 127*(3), 240–248. https://doi.org/10.1016/j.mad.2005.10.004

Levine, M. E. (2013). Modeling the rate of senescence: Can estimated biological age predict mortality more accurately than chronological age? *The Journals of Gerontology: Series A: Biological Sciences and Medical Sciences, 68*(6), 667–674. https://doi.org/10.1093/gerona/gls233

Levine, M. E., Lu, A. T., Chen, B. H., Hernandez, D. G., Singleton, A. B., Ferrucci, L., Bandinelli, S., Salfati, E., Manson, J. E., Quach, A., Kusters, C. D. J., Kuh, D., Wong, A., Teschendorff, A. E., Widschwendter, M., Ritz, B. R., Absher, D., Assimes, T. L., Horvath, S., & others. (2018). An epigenetic biomarker of aging for lifespan and healthspan. *Aging, 10*(4), 573–591. https://doi.org/10.18632/aging.101414

Liu, Z., Kuo, P.-L., Horvath, S., Crimmins, E., Ferrucci, L., & Levine, M. E. (2018). A new aging measure captures morbidity and mortality risk across diverse subpopulations from NHANES IV: A cohort study. *PLoS Medicine, 15*(12), e1002718. https://doi.org/10.1371/journal.pmed.1002718

---

## NHANES Data Sources

Centers for Disease Control and Prevention. (n.d.). *National Health and Nutrition Examination Survey (NHANES).* https://www.cdc.gov/nchs/nhanes/

Centers for Disease Control and Prevention. (n.d.). *NHANES Analytic Guidelines.* https://wwwn.cdc.gov/nchs/nhanes/analyticguidelines.aspx

Centers for Disease Control and Prevention. (n.d.). *NHANES Laboratory Procedures Manuals.* https://wwwn.cdc.gov/nchs/nhanes/

National Center for Health Statistics. (n.d.). *NHANES Survey Methods and Analytic Guidelines.*

---

## Methodological Standards

American Psychological Association. (2020). *Publication manual of the American Psychological Association* (7th ed.). American Psychological Association.

Page, M. J., McKenzie, J. E., Bossuyt, P. M., Boutron, I., Hoffmann, T. C., Mulrow, C. D., Shamseer, L., Tetzlaff, J. M., Akl, E. A., Brennan, S. E., Chou, R., Glanville, J., Grimshaw, J. M., Hróbjartsson, A., Lalu, M. M., Li, T., Loder, E. W., Mayo-Wilson, E., McDonald, S., ... Moher, D. (2021). The PRISMA 2020 statement: An updated guideline for reporting systematic reviews. *BMJ, 372*, n71. https://doi.org/10.1136/bmj.n71

Wilkinson, M. D., Dumontier, M., Aalbersberg, I. J., Appleton, G., Axton, M., Baak, A., Blomberg, N., Boiten, J.-W., da Silva Santos, L. B., Bourne, P. E., Bouwman, J., Brookes, A. J., Clark, T., Crosas, M., Dillo, I., Dumon, O., Edmunds, S., Evelo, C. T., Finkers, R., ... Mons, B. (2016). The FAIR Guiding Principles for scientific data management and stewardship. *Scientific Data, 3*, 160018. https://doi.org/10.1038/sdata.2016.18

---

## Software and Computational Resources

Kuo, P.-L., Schrack, J. A., Levine, M. E., Moore, A. Z., An, Y., Elango, P., Karikkineth, A. C., Tanaka, T., & Ferrucci, L. (2021). *BioAge: An R package for quantifying biological age from clinical biomarkers*. GitHub. https://github.com/dayoonkwon/BioAge

Semantic Versioning. (2013). *Semantic Versioning 2.0.0*. https://semver.org/

Wickham, H., Çetinkaya-Rundel, M., & Grolemund, G. (2023). *R for Data Science* (2nd ed.). O'Reilly Media.

---

## Supporting Literature

Belsky, D. W., Caspi, A., Houts, R., Cohen, H. J., Corcoran, D. L., Danese, A., Harrington, H., Israel, S., Levine, M. E., Schaefer, J. D., Sugden, K., Williams, B., Yashin, A. I., Poulton, R., & Moffitt, T. E. (2015). Quantification of biological aging in young adults. *Proceedings of the National Academy of Sciences, 112*(30), E4104–E4112. https://doi.org/10.1073/pnas.1506264112

Preston, S. H., Heuveline, P., & Guillot, M. (2001). *Demography: Measuring and Modeling Population Processes*. Blackwell Publishing.