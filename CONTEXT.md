# Simple AI App

A small recipe app that the instructor demonstrates in the lecture and students run themselves afterwards, before they open the Book Manager. It shows one idea: model output is a suggestion that a person must confirm before it becomes a record.

## Language

### Records

**Recipe**:
A saved dish with a name, one or more **Ingredients**, and an optional prep time. Only a **Recipe** is ever stored, and it does not record whether it came from **Manual Entry** or a **Draft**.
_Avoid_: Menu, dish record

**Ingredient**:
One line of a **Recipe**: a name, an **Amount** and a **Unit**. Belongs to exactly one **Recipe**.
_Avoid_: Item, component

**Unit**:
One entry from the fixed list of allowed measures. Each measure is one **Unit**, named in Thai with an English label, such as ช้อนโต๊ะ (tbsp); "tbsp", "Tbsp." and "ช.ต." all mean that one **Unit**. A unit outside the list makes a **Draft** a **Rejected Draft**.
_Avoid_: Measure, free-text unit, tbsp and ช้อนโต๊ะ as two units

**Amount**:
How much of an **Ingredient**, in its **Unit**. It may be a fraction, such as half a ถ้วย. Required for every **Unit** except **To Taste**.
_Avoid_: Quantity, number

**To Taste**:
The special **Unit** for "add as much as you like" (ตามชอบ). It also covers "a pinch" and เล็กน้อย. It has no **Amount**.
_Avoid_: Optional amount, no unit

### Getting a Recipe in

**Manual Entry**:
Creating a **Recipe** by typing into the recipe form. The same input always produces the same **Recipe**.
_Avoid_: Normal create, CRUD form

**Recipe Text**:
The messy text a person pastes, such as a blog post, a social media post or a video caption. It is the only source of facts for an **Extraction**.
_Avoid_: Prompt, input, description

**Extraction**:
Asking the model to turn **Recipe Text** into a **Draft**. The same **Recipe Text** can give a different **Draft** each time.
_Avoid_: Generation, AI create, autofill

**Draft**:
The model's structured suggestion from one **Extraction**. A **Draft** is never stored as a **Recipe**; it only pre-fills the recipe form.
_Avoid_: Result, AI recipe, output

**Review**:
A person checking and correcting a **Draft** in the recipe form, with the **Recipe Text** beside it, then saving it. **Review** is the only way a **Draft** becomes a **Recipe**.
_Avoid_: Approval, confirm step

**Comparison**:
Several **Extractions** of the same **Recipe Text** shown side by side, with differing fields highlighted. A **Comparison** is only for looking; none of its **Drafts** can go to **Review**.
_Avoid_: Compare runs, batch extraction, multi-run

### When the model goes wrong

**Rejected Draft**:
A **Draft** that breaks a recipe rule, such as an unknown **Unit**. It still goes to **Review**, with the wrong values kept and marked, and cannot be saved until they are fixed.
_Avoid_: Bad output, failed extraction, error

**Fallback**:
What a person gets when an **Extraction** gives no **Draft** at all, because the model timed out or failed on every attempt: an empty recipe form with their **Recipe Text** kept and a reason shown. A **Rejected Draft** is not a **Fallback**.
_Avoid_: Error page, retry screen

### Running the demo

**Demo Switch**:
A control that forces one model behaviour on demand, so a failure appears the same way every time even though the real model is used. The switches are **Slow**, **Hang**, **Error** and **Bad Unit** (which makes any **Draft** a **Rejected Draft**). The per-attempt timeout is set here too.
_Avoid_: Feature flag, toggle, debug mode

**Provider**:
The one doorway through which every **Extraction** reaches the model. **Demo Switches**, timeouts and retries all apply here.
_Avoid_: Client, LLM, backend

**Sample**:
A prepared **Recipe Text** shipped with the demo, chosen to cause one specific behaviour, such as a natural **Rejected Draft** or a made-up recipe from text that is not a recipe.
_Avoid_: Fixture, example, seed text

### Hands-on

**Worksheet**:
The first hands-on exercise: students use the finished app, run **Samples**, make a **Comparison** and flip **Demo Switches**, and write down what they see. No coding.
_Avoid_: Lab sheet, exercise 1

**Gap**:
One function students write in the second hands-on exercise, with failing tests that describe it. There are three, done in order: validating a **Draft**, **Extraction** with timeout and retry, and choosing between a **Draft**, a **Rejected Draft** and a **Fallback**.
_Avoid_: TODO, task, blank

**Starter**:
The version of the **Gaps** with the functions left for students to write. Only the **Gaps** differ between **Starter** and **Solution**; the rest of the app is shared.
_Avoid_: Template, skeleton, student version

**Solution**:
The version of the **Gaps** with the functions complete. The **Worksheet** runs on it, and students may read it when stuck.
_Avoid_: Answer key, reference, finished app

## Example dialogue

> **Dev:** When extraction succeeds, do we save the recipe straight away?
> **Instructor:** No. An **Extraction** only gives a **Draft**. It fills the form, and the **Review** decides what gets saved.
> **Dev:** So a saved **Recipe** looks the same whether it came from **Manual Entry** or a **Draft**?
> **Instructor:** Yes. Both finish with the same form submit. That's the point of the demo: the non-deterministic part ends at the **Draft**.

## Flagged ambiguities

- "Recipe" was used for both the model's JSON and the saved row. Resolved: the model's JSON is a **Draft**; only the saved row is a **Recipe**.
- "Quantity" in the early scripts meant a whole number. Resolved: the term is **Amount**, and "to taste" is the **To Taste** unit, not a missing amount.
- A model that writes "1 tsp" where the **Recipe Text** said "ตามชอบ" produces a valid **Draft** that is still wrong. Only **Review** can catch this.
- "A pinch" and เล็กน้อย could have been their own **Units**. Resolved: both are **To Taste**.
- An early design had a **Mock** provider inside the app. Resolved: there is no **Mock**; every **Extraction** uses the real model, and **Demo Switches** force failures.
- Live runs showed the model often turns an unknown unit into an allowed one, so a **Sample** alone cannot be relied on to produce a **Rejected Draft**. The **Bad Unit** switch exists for that.
