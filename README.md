# phantoms-ai-week7
# Phantoms | W7D2 - Chunking Experiment

## 1. الأسئلة العشرة
* **Q1 (مباشر 1):** What is the Primary Key in the given unnormalized table?
* **Q2 (مباشر 2):** Why does the table satisfy 1NF?
* **Q3 (مباشر 3):** Why is partial dependency impossible in this table when checking 2NF?
* **Q4 (مباشر 4):** What are the three database anomalies mentioned when storing JobTitle directly?
* **Q5 (مباشر 5):** Which attribute acts as a Foreign Key in the Employees table after redesigning for 3NF?
* **Q6 (متفرق 1):** How does JobID relate to JobTitle in the original table, and how is that relationship separated in the 3NF redesign?
* **Q7 (متفرق 2):** Which employees have JobID J01, what are their salaries, and how are they represented in the normalized 3NF tables?
* **Q8 (متفرق 3):** How does moving from the original table to the 3NF schema solve data repetition and update problems?
* **Q9 (غير موجود 1):** How do you write a SQL query using a LEFT JOIN and window functions to rank employees by salary per department?
* **Q10 (غير موجود 2):** What are the best practices for configuring Kubernetes autoscaling policies for a high-traffic microservice?

## 2. جدول مقارنة النتائج (10 أسئلة × 3 إعدادات)
| السؤال | إعداد صغير (140 / Overlap 30) | إعداد متوسط (500 / Overlap 100) | إعداد كبير (1500 / Overlap 250) |
| :--- | :--- | :--- | :--- |
| **Q1** | نعم (#1) | نعم (#1) | نعم (#1) |
| **Q2** | نعم (#2) | نعم (#1) | نعم (#1) |
| **Q3** | نعم (#1) | نعم (#1) | نعم (#1) |
| **Q4** | لا (انقسمت الأنومليز) | نعم (#1) | نعم (#1) |
| **Q5** | نعم (#2) | نعم (#1) | نعم (#1) |
| **Q6 (متفرق)** | لا | نعم (#1) | نعم (#1) |
| **Q7 (متفرق)** | لا | نعم (#1) | نعم (#1) |
| **Q8 (متفرق)** | لا | نعم (#2) | نعم (#1) |
| **Q9 (غير موجود)** | غير متوفرة (مسافة عالية) | غير متوفرة (مسافة عالية) | غير متوفرة (مسافة عالية) |
| **Q10 (غير موجود)** | غير متوفرة (مسافة عالية) | غير متوفرة (مسافة عالية) | غير متوفرة (مسافة عالية) |

## 3. الخلاصة وأسوأ حالة فشل
الإعداد المتوسط (حجم 500 مع Overlap 100) هو الأنسب لأنه يحافظ على اكتمال المعنى وسياق الإجابة دون تشتيت مثل الحجم الصغير أو حشو زائد مثل الحجم الكبير. أما أسوأ حالة فشل فظهرت في الإعداد الصغير (140) مع الأسئلة ذات الإجابة الموزعة مثل Q6 وQ7، حيث أدى صغر حجم القطعة إلى تقسيم المعلومة وفقدان الترابط الكامل بين أجزاء الإجابة.
