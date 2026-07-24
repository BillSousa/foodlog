# Setup Wizard

Multi-step, installer-style flow shown on first launch of a new project 
or after a project is reset ("Set-up Wizard toggle" is in "not set up" 
position). Only the Nutrient Tracking step is mandatory — every other 
step can be skipped and revisited later via the Main GUI.

## Step 1 — Welcome

```
┌──────────────────────────────────────────────────────────┐
│  WELCOME TO FOODLOG                          [Step 1 of 5]│
├──────────────────────────────────────────────────────────┤
│                                                            │
│   This wizard will help you set up a new FoodLog          │
│   project. You'll choose which nutrients to track,        │
│   optionally set up categories, set a daily calorie        │
│   target, and optionally start entering items.             │
│                                                            │
│   Everything except nutrient tracking can be skipped       │
│   and changed later.                                       │
│                                                            │
│                                        [ Next → ]          │
└──────────────────────────────────────────────────────────┘
```

## Step 2 — Nutrient Tracking (MANDATORY — no skip button)

```
┌──────────────────────────────────────────────────────────┐
│  NUTRIENT TRACKING                           [Step 2 of 5]│
├──────────────────────────────────────────────────────────┤
│  Choose which nutrients you want to track. This           │
│  determines what nutrients you need to enter from food     |    
|  labels when you enter a new food, and what nutrients you  |
|  can analyze in "Reporting". You can change this anytime   |
|  later via "Manage Tracked Nutrients." Not selecting any   |
|  nutrients is allowed --- FoodLog will only track purchase |
|  dates, items purchased, quantities purchased, consumption |
|  entry dates, items consumed, and amounts consumed.        │
│                                                            │
│                                                            │
│  [X] Calories        [X] Sodium        [ ] Ethanol         │
│  [X] Total Fat        [X] Fiber        [ ] Glycemic Index  │
│  [X] Protein          [X] Total Carbs                      │
│                                                            │
│  Vitamins & Minerals:      [ ] Track All Vitamins/Minerals │
│  [ ] Vitamin D   [ ] Vitamin A   [ ] Vitamin C   [ ] ...    │
│  [ ] Calcium     [ ] Iron        [ ] Potassium  [ ] ...    │
│  (scrollable — full ~21 optional list)                    │
│                                                            │
│              [ ← Back ]              [ Next → ]            │
└──────────────────────────────────────────────────────────┘
```
No "Skip" button on this step — it is the one forced decision point in
the app. An all-unchecked configuration (besides whatever a user leaves on)
is still valid.

## Step 3 — Categories (optional)

```
┌──────────────────────────────────────────────────────────┐
│  CATEGORIES (OPTIONAL)                       [Step 3 of 5]│
├──────────────────────────────────────────────────────────┤
│  You can create categories now (e.g. "Pasta," "Meat,"    │
│  "Dairy") to group items when shopping and reporting, or │
│  skip this and do it later via "Manage Categories."       │
│                                                            │
│  New category name: [______________]  [ Add ]              │
│                                                            │
│  Categories so far:                                        │
│    • Pasta                                    [ Remove ]   │
│    • Baking                                    [ Remove ]   │
│    (none required — list can stay empty)                   │
│                                                            │
│         [ ← Back ]     [ Skip → ]     [ Next → ]           │
└──────────────────────────────────────────────────────────┘
```

## Step 4 — Cal/Day Target

```
┌──────────────────────────────────────────────────────────┐
│  DAILY CALORIE TARGET                        [Step 4 of 5]│
├──────────────────────────────────────────────────────────┤
│  This target is used to estimate how many days an order    │
│  will last, and drives per-day figures in Reporting.        │
│  You can change this anytime later via Settings.            │
│                                                            │
│              Target calories per day: [ 2000 ]              │
│                                                            │
│                                                            │
│              [ ← Back ]              [ Next → ]            │
└──────────────────────────────────────────────────────────┘
```
Default pre-filled at 2000; user may override.

## Step 5 — Populate Items (optional, final step)

```
┌──────────────────────────────────────────────────────────┐
│  POPULATE ITEMS                              [Step 5 of 5]│
├──────────────────────────────────────────────────────────┤
│  Would you like to start entering food items now, or       │
│  skip this and do it later from the main screen?            │
│                                                            │
│                                                            │
│      [ Skip — Go to Main Screen ]                          │
│      [ Start Entering Items → ]                             │
│                                                            │
│              [ ← Back ]                                    │
└──────────────────────────────────────────────────────────┘
```
"Start Entering Items" exits the wizard directly into the Manage Items
screen. "Skip" exits directly into the Main GUI. Either choice ends the
wizard permanently for this project — it does not reappear on subsequent
launches (the project is no longer "new" once this completes, the "Set-up 
Wizard toggle" is moved to the "set up" position).
