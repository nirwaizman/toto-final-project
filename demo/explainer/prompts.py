STYLE = ("editorial paper cut-out motion graphics: textured cream paper background with faint fibers, "
 "every object a flat cut-out illustration with thin dark outlines and muted engraved crosshatch shading, "
 "one bold flat deep-magenta accent circle per scene, gentle collage layering with soft drop shadows, "
 "generous negative space, restrained palette (cream, charcoal, wood-brown, deep magenta, one navy accent), "
 "non-photorealistic, illustrated, not a photo, no live-action, no realism")
TOTO = ("TOTO the mascot — a small friendly paper cut-out robot-dog: rounded white paper body with thin dark outline, "
 "navy-blue ear tips, a tiny orange collar light, two round dot eyes, closed mouth, simple readable silhouette, same design every time")
NEG = ("color drift, photorealism, glossy 3D render, real people, live-action, lip-sync, mouth movement, captions, on-screen text, letters, numerals, logos, watermark, neon, gradients")
def block(scene, motion, audio):
    return (f"STYLE REFERENCE: Match the attached reference image EXACTLY. Replicate its look precisely: {STYLE}. "
            f"Every element below rendered in that identical style.\nSCENE: {scene}\nMOTION: {motion}\n"
            f"AUDIO: {audio} — no voice, dialogue, or narration.\nNEGATIVE: {NEG}.")
P = {
1: block(f"MEDIUM shot. {TOTO} stands centered on the cream paper stage in front of a big deep-magenta circle and greets the viewer with a slow friendly paw wave, mouth closed. Around him drift small paper cut-out hotel key cards, luggage tags and booking tickets.",
         "Motion from frame one: slow push-in on Toto; tickets float and rotate gently; the magenta circle scales up subtly.",
         "soft paper rustle, light warm ambient pad"),
2: block("WIDE lateral shot of a long row of paper cut-out hotel room doors on the cream paper stage. One after another, every third door's cut-out 'booked' tag flips over and that door fades to gray, torn-paper edges appearing, leaving empty gaps. A deep-magenta circle sits behind the row.",
         "Continuous slow lateral pan along the doors while tags flip and doors dim in sequence; a paper coin drops and rolls out of frame.",
         "paper flips, a soft coin clink, low quiet hum"),
3: block("HIGH-ANGLE overhead shot. Seven small paper cut-out figurines with simple tool icons (magnifier, broom, chart, quill, checkmark, gears, trophy) are arranged in two groups: four on the right, three on the left, on the cream stage. A wide paper arrow slides from the group of four to the group of three, and the figurines nudge and pass a paper folder along the line.",
         "Slow overhead drift; the arrow extends across the gap; figurines bob and pass the folder hand to hand.",
         "paper sliding, gentle tick-tock rhythm"),
4: block("CLOSE-UP. A giant paper spreadsheet scroll unrolls across the stage: a grid of tiny cut-out cells with faint engraved marks. A paper magnifying glass cut-out sweeps across the columns and cells light up in deep magenta one by one; small tally tiles flip on the side.",
         "Scroll unrolls from frame one; magnifier sweeps left to right; camera tracks with it, slight tilt.",
         "paper unrolling, soft flip clicks"),
5: block("MEDIUM shot. A paper broom cut-out sweeps torn scraps and crumpled cells off the spreadsheet into a paper bin. Then two tall paper bars rise from the stage: a taller charcoal 'city hotel' bar with a deep-magenta highlight cap and a shorter wood-brown 'resort' bar; a small paper hotel-building icon sits on each bar.",
         "Broom sweeps first, then hard contrast cut to the two bars growing upward with a slight overshoot bounce; slow push-in on the taller bar.",
         "sweeping paper, two soft rising whooshes"),
6: block(f"MEDIUM shot. A paper contract scroll rolls open on the stage with a deep-magenta wax-seal circle; a paper quill cut-out draws crisp lines and a checklist of small boxes; beside it a fan of paper insight cards with tiny bar and pie icons spreads out. {TOTO} peeks in from the corner and nods.",
         "Scroll rolls out from frame one; quill glides; cards fan open; slow drift left to right.",
         "quill scratching on paper, cards fanning"),
7: block(f"WIDE shot. A paper turnstile gate divides the stage into two zones. A contract card slides toward the gate; a paper stamp cut-out presses down and leaves a bold checkmark; the gate arms turn and the card passes. Then a second card with a torn corner arrives; the stamp leaves an orange-red X shape and the card bounces back and drops into a bin. {TOTO} stands beside the gate as gatekeeper, raising a paw to stop it.",
         "Cards slide, stamp presses with a satisfying squash, gate rotates; hard contrast beat on the rejection; slight camera shake on the X stamp.",
         "stamp thumps, gate click, paper bounce"),
8: block("LOW-ANGLE shot. A paper funnel hovers over the stage; a stream of column cards flows in from above. Most cards pass through the funnel and snap into a neat feature table below, while two cards marked with a stop-octagon shape are deflected sideways into a bin. The table assembles row by row.",
         "Cards stream continuously from frame one; funnel wobbles gently; camera slowly tilts up from the table to the funnel.",
         "papery whooshes, soft snaps as cards lock into the table"),
9: block("WIDE shot, two paper machines side by side on the stage: on the left a cluster of tiny cut-out trees on a platform, on the right a staircase of ascending paper arrows; a long paper timeline strip with calendar-page icons feeds into both machines. A separate, shorter timeline strip with a deep-magenta circle marker slides in from the far right, ready to test them.",
         "Timeline strip feeds in continuously; machines chug and bob; the test strip slides in late; slow lateral drift right.",
         "soft mechanical clicks, paper conveyor rustle"),
10: block("CLOSE-UP. A paper ribbon rosette lands on the arrow-staircase machine; a paper gauge dial with a needle sweeps up close to the top and settles; a report page slides in beside it with rows of paper bars growing to different lengths.",
          "Rosette drops with a bounce; needle sweeps smoothly; bars grow in staggered rhythm; slow push-in on the gauge.",
          "a soft chime, paper bars sliding"),
11: block(f"MEDIUM shot. A paper card folds open like an ID card into three panels with icons: a target, a warning triangle, and a shield with a heart. Below, a small paper guest silhouette stands calmly while {TOTO} places a paw gently in front of it, protective and kind.",
          "Card folds open panel by panel from frame one; icons pop with slight bounce; slow drift; Toto's paw moves slowly.",
          "paper folding, warm soft pad"),
12: block(f"WIDE pull-out shot. A paper laptop cut-out opens on the stage showing a dashboard of blocks and a dial; {TOTO} beside it presses a paper button, the dial needle swings and a small deep-magenta circle lights up on the screen. Then Toto turns to camera and waves goodbye with a slow paw wave, mouth closed, as the seven tiny figurines gather behind him.",
          "Laptop opens from frame one; needle swings; slow pull-out to wide as figurines gather; final wave held.",
          "gentle click, warm resolving chord, paper rustle"),
}
if __name__=="__main__":
    import json; json.dump(P, open("prompts.json","w"), indent=1)
    for k,v in P.items(): print(f"Block {k}\n{v}\n")
