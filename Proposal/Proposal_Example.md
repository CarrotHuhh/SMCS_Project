## 1. Introduction & Motivation (½–¾ page)

### Purpose of this section

Convince the reader **this problem matters** and **your approach is reasonable**.

### What to include

1. **Context**
   - Public transport reliability is critical in the Netherlands
   - Bus delays and cancellations reduce passenger trust and usability
2. **Concrete problem**
   - A significant fraction of cancellations are due to **driver shortages**
   - Shortages are uneven across **routes and time periods**
3. **Why current practice is limited**
   - Fixed driver–route assignments
   - Limited use of data-driven, short-term reallocation
4. **Your key idea (1–2 sentences)**
   - Use historical data to identify **high-risk route–time combinations**
   - Reallocate a *small number of drivers* to reduce cancellations

### What NOT to include

- Detailed algorithms
- Literature survey (keep that for later)

------

## 2. Problem Definition (½ page)

### Purpose

Make the problem **precise and bounded**.

### Structure

#### 2.1 System abstraction

Explain your simplifications explicitly.

Example points:

- Time is discretized into hourly intervals
- Drivers are treated as identical resources
- Decisions are made at the route–hour level

#### 2.2 Input and output

- **Inputs**
  - Scheduled trips per route and hour
  - Historical cancellation / delay data
- **Output**
  - A reallocation plan indicating how many drivers are assigned to each route per hour

#### 2.3 Objective

State one clear objective.

Example:

> Minimize the expected number of cancelled bus trips under a limited driver supply.

------

## 3. Scope and Assumptions (½ page — very important)

This section **increases credibility**.

### Typical assumptions to list

- Driver availability per hour is fixed
- All drivers are qualified for all routes
- Reallocation decisions are made offline (not real-time)
- Passenger demand is not influenced by short-term changes

### Why this matters

Explicit assumptions:

- Prevent overclaiming
- Show awareness of real-world complexity
- Protect you from criticism

------

## 4. Data Collection & Sources (½ page)

### Purpose

Show the project is **feasible with available data**.

### Suggested subsections

#### 4.1 Data sources

List concrete datasets:

- GTFS static schedules
- Real-time or historical AVL / GTFS-RT
- Optional: passenger counts or weather

#### 4.2 Data granularity

- Route-level
- Hourly aggregation
- Time span (e.g., several months or years)

#### 4.3 Data preprocessing (high level)

- Matching scheduled and observed trips
- Identifying cancelled or missing trips
- Aggregating statistics per route–hour

Avoid implementation details here.

------

## 5. Methodology Overview (½–¾ page)

### Purpose

Explain *what you plan to do*, not how every line works.

### Structure

#### 5.1 Risk estimation

- Predict the probability of cancellation per route–hour
- Use simple ML models (e.g., logistic regression)

#### 5.2 Driver reallocation strategy

- Use predicted risk to prioritize routes
- Reassign a limited number of drivers from low-risk to high-risk routes
- Optimization or greedy allocation

Keep this conceptual, not mathematical.

------

## 6. Evaluation Plan (½ page)

### Purpose

Convince the reader you can **measure success**.

### What to include

- Offline evaluation using historical data
- Baselines:
  - No reallocation
  - Rule-based allocation
- Metrics:
  - Number of cancelled trips
  - Relative improvement (%)
- Sub-analyses:
  - Peak vs off-peak hours

------

## 7. Expected Contributions (¼ page)

### Example points

- A simple, interpretable framework for driver reallocation
- Evidence that even limited reallocation can reduce cancellations
- A reproducible methodology using public transit data

Avoid overstating impact.

------

## 8. Limitations & Future Work (¼ page)

### This section scores you “maturity points”

Typical limitations:

- Simplified driver model
- No real-time deployment
- No passenger behavior modeling

Future extensions:

- Driver-level constraints
- Real-time dispatch
- Fairness-aware optimization

------

## 9. Timeline (optional, short)

------

## 10. References (if required)

- GTFS documentation
- A small number (2–4) of relevant transport or ML papers