Please implement the following enhancements to the college coursework and transfer-credit workflow.

A CSV file named `Regionally_Accredited_Institution.csv` will be provided and should be used as the source of truth for school accreditation classification.

These changes should be configuration-driven where possible and should integrate with the existing lead qualification flow.

## CSV Mapping Requirements

Use the following columns from `Regionally_Accredited_Institution.csv`:

* Column D (`INSTNM`) = Institution Name
* Column H (`ACCREDAGENCY`) = Accreditation Agency

The institution dropdown/search should be populated using the institution names from Column D.

Accreditation classification should be determined using the accreditation value from Column H.

### Regional Accreditation Rules

A school should be considered **Regionally Accredited** if its `ACCREDAGENCY` value is one of the following:

* Southern Association of Colleges and Schools Commission on Colleges
* Higher Learning Commission
* Northwest Commission on Colleges and Universities
* Western Association of Schools and Colleges Accrediting Commission for Community and Junior Colleges
* Western Association of Schools and Colleges Senior Colleges and University Commission
* New England Commission on Higher Education
* Middle States Commission on Higher Education

All other accreditation values should be treated as **Nationally Accredited / Not Regionally Accredited**, unless explicitly overridden by future configuration.

If the accreditation value is:

* NA
* Blank
* EXEMPT
* Unknown

then classify the institution as **Not Regionally Accredited**.

---

## 1. Step 3: College Attendance Question

Add the following question in Step 3:

**Have you attended college before?**

Options:

* Yes
* No

If the lead selects **No**, continue the standard workflow.

If the lead selects **Yes**, proceed to collect prior college information.

---

## 2. Prior College Selection

When a lead indicates they have attended college:

1. Allow them to search/select institutions from `Regionally_Accredited_Institution.csv`.
2. Use Column D (`INSTNM`) as the displayed school name.
3. Allow multiple schools if the workflow currently supports multiple institutions.
4. Include an **Other** option.

---

## 3. "Other" School Option

When the user selects:

**Other**

assume the institution is **Nationally Accredited / Not Regionally Accredited** unless future business rules specify a different process.

This option should trigger the same workflow behavior as other non-regionally accredited institutions.

---

## 4. Accreditation Determination

After school selection:

1. Locate the selected institution in `Regionally_Accredited_Institution.csv`.
2. Read the accreditation value from Column H (`ACCREDAGENCY`).
3. Determine whether the school is:

   * Regionally Accredited
   * Nationally Accredited / Not Regionally Accredited

Store this classification for workflow decisions and auditing purposes.

---

## 5. Skip Transfer Evaluation for Nationally Accredited Schools

If all selected institutions are classified as Nationally Accredited / Not Regionally Accredited:

Skip:

* CBE course evaluation
* Science prerequisite evaluation
* Science course recency validation
* Course transferability review

No additional transfer-credit questions should be displayed.

---

## 6. Required User Disclosure

Before skipping the transfer evaluation workflow, display the following message:

"The school(s) you attended are not regionally accredited. Based on current transfer policies, coursework from these institutions generally cannot be transferred toward the programs we evaluate. Because of this, we will not ask you additional questions about your completed coursework."

The user must see this explanation before the workflow continues.

---

## 7. Mixed Accreditation Scenarios

If the lead attended both regionally accredited and nationally accredited institutions:

* Continue transfer evaluation only for coursework from regionally accredited institutions.
* Do not evaluate coursework from nationally accredited institutions.
* Continue normal prerequisite and transferability review for regionally accredited coursework.
* Ignore nationally accredited coursework during transfer-credit determination.

---

## 8. CBE Minimum Grade Requirement

For any course being evaluated for transfer credit:

Minimum acceptable grade:

* C

Business Rules:

A course is eligible for transfer consideration only if:

* The institution is regionally accredited.
* The earned grade is C or higher.

If the grade is below C:

* Do not award transfer consideration.
* Do not satisfy prerequisite requirements.
* Flag the course as non-transferable.

Display:

"To receive transfer credit consideration for this course, a minimum grade of C is required. Based on the information provided, this course may not be eligible for transfer."

---

## Database / Schema Changes

Please add fields as needed to support:

* Institution Name
* Accreditation Agency
* Accreditation Type

  * Regionally Accredited
  * Nationally Accredited / Not Regionally Accredited
* Accreditation Source
* Transfer Evaluation Eligible (boolean)
* Grade Validation Result
* Transfer Eligibility Result

---

## Expected Workflow Logic

1. Ask if the lead has attended college.

2. If No:

   * Continue existing workflow.

3. If Yes:

   * Allow institution selection from `Regionally_Accredited_Institution.csv`.
   * Allow "Other".

4. Determine accreditation using:

   * Column D (`INSTNM`)
   * Column H (`ACCREDAGENCY`)

5. If all institutions are Nationally Accredited / Not Regionally Accredited:

   * Display disclosure message.
   * Skip transfer-credit workflow.
   * Continue remainder of lead qualification flow.

6. If one or more institutions are Regionally Accredited:

   * Continue transfer-credit workflow.
   * Evaluate eligible coursework.
   * Apply science prerequisite rules.
   * Apply science recency rules.
   * Enforce minimum grade of C.

7. For mixed-accreditation scenarios:

   * Evaluate only coursework from regionally accredited institutions.
   * Exclude nationally accredited institutions from transfer-credit consideration.

---

## Deliverables

Please provide:

* Affected workflow components
* UI changes required
* Database/schema changes required
* CSV ingestion/mapping updates
* Configuration changes
* Validation rules
* Test cases covering:

  * No prior college attendance
  * Regional-only institutions
  * National-only institutions
  * Mixed institutions
  * Other selection
  * Unknown accreditation values
  * NA accreditation values
  * EXEMPT accreditation values
  * Grade C and above
  * Grade below C
