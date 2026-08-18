"""Build Hebrew SRT for the explainer: one caption pair per 10s block, timed to the
(possibly tempo-adjusted) voice take that is centered inside its block."""
import json, subprocess, sys
HE = {
1: ["הכירו את Toto. עוזר AI קטן שמנהל צוות נתונים שלם,", "והופך הזמנות מלון מבולגנות לחיזויים — עוד לפני הצ'ק-אין."],
2: ["הנה הבעיה: יותר מהזמנה אחת מכל שלוש מתבטלת.", "חדרים ריקים, כוח אדם מבוזבז, והכנסה שאובדת כל יום."],
3: ["הפרויקט מדמה צוות מוצר AI אמיתי:", "שבעה סוכנים מתמחים בשני צוותים, שמעבירים עבודה זה לזה אוטומטית."],
4: ["צוות אחת הוא אנליסט הנתונים. הסוכן הראשון טוען", "יותר מ-119 אלף הזמנות אמיתיות ומפיק פרופיל לכל עמודה."],
5: ["סוכן ניקוי מתקן ערכים חסרים ומסיר שורות שבורות.", "ואז אנליסט צולל פנימה: מלונות עירוניים מבטלים 42% מההזמנות."],
6: ["האנליסט האחרון כותב תובנות עסקיות וחוזה נתונים פורמלי —", "הבטחה קריאה-למכונה על מה שהנתונים באמת מכילים."],
7: ["עכשיו נכנס ה-Flow. שער ולידציה בודק את החוזה מול הנתונים האמיתיים.", "אם משהו לא תקין — הכל נעצר שם."],
8: ["צוות שתיים הוא מדען הנתונים. הוא מאמת שוב את החוזה, בונה פיצ'רים,", "ומשאיר בחוץ בזהירות כל מה שידוע רק אחרי התוצאה."],
9: ["שני מודלים מתחרים: Random Forest מול Gradient Boosting,", "מאומנים על 2015–2016 ונבחנים על 2017."],
10: ["Gradient Boosting מנצח, עם ROC-AUC של 0.875.", "כל מדד נכתב לדוח שקוף."],
11: ["Model Card מסביר למה המודל נועד, מה מגבלותיו ומה האתיקה שלו:", "לתמוך בהחלטות תכנון — לעולם לא לשפוט אורח בודד."],
12: ["ולבסוף, אפליקציית Streamlit מריצה את כל ה-Flow ומספקת חיזויים חיים.", "זה Toto: סוכנים מתמחים, העברות מאומתות, החלטות אמיתיות."],
}
def ts(t):
    h=int(t//3600); m=int(t%3600//60); s=int(t%60); ms=int(round((t-int(t))*1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
def main(timing_json, out_srt):
    timing=json.load(open(timing_json))  # {block: {"start": offset within block, "dur": voiced duration}}
    lines=[]; idx=1
    for b in range(1,13):
        base=(b-1)*10.0; st=base+timing[str(b)]["start"]; du=timing[str(b)]["dur"]
        # split caption pair proportionally
        l1,l2=HE[b]; w1=len(l1); w2=len(l2); split=st+du*w1/(w1+w2)
        for (a,z,txt) in [(st,split-0.05,l1),(split,st+du,l2)]:
            lines.append(f"{idx}\n{ts(a)} --> {ts(z)}\n{txt}\n"); idx+=1
    open(out_srt,"w",encoding="utf-8").write("\n".join(lines))
    print("wrote",out_srt,idx-1,"cues")
if __name__=="__main__": main(sys.argv[1], sys.argv[2])
