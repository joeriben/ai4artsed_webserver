#!/usr/bin/env python3
"""
Script to add "über" and "about" nodes to workflow files
"""
import json
from pathlib import Path

# Define the text content for each workflow
workflow_texts = {
    # ACROSS
    "ai4artsed_ImageAndSound_2506270842.json": {
        "über": "Bild und Klang\nErzeugt gleichzeitig Bild und Audio aus einem Prompt\nDieser Workflow generiert sowohl ein Bild als auch eine passende Audiodatei aus einem einzigen Prompt für multimediale Kunstprojekte.",
        "about": "Image and Sound\nGenerates both image and audio from a single prompt\nThis workflow creates both an image and matching audio file from one prompt for multimedia art projects."
    },
    "ai4artsed_ImageToSound_2506270842.json": {
        "über": "Bild zu Klang\nWandelt Bildbeschreibungen in Klanglandschaften um\nTransformiert visuelle Prompts in akustische Interpretationen. Der Workflow analysiert die Elemente einer Bildbeschreibung und erzeugt daraus Soundscapes oder Musik.",
        "about": "Image to Sound\nConverts image descriptions into soundscapes\nTransforms visual prompts into acoustic interpretations. The workflow analyzes elements of an image description and creates soundscapes or music."
    },
    
    # AESTHETICS
    "ai4artsed_ClichéFilter_V1_2506160013.json": {
        "über": "Klischee-Filter V1\nErkennt klischeehafte Bildmotive und verfolgt verschiedene Strategien, Klischees zu vermeiden\nV1: Direkte Inversion von Klischees. V2: Kontextuelle Neuinterpretation. V3: Kombination beider Ansätze mit verstärktem Negativprompt für maximale Klischee-Vermeidung.",
        "about": "Cliché Filter V1\nDetects clichéd image motifs and pursues different strategies to avoid clichés\nV1: Direct inversion of clichés. V2: Contextual reinterpretation. V3: Combination of both approaches with enhanced negative prompt for maximum cliché avoidance."
    },
    "ai4artsed_ClichéFilter_V2_2506211602.json": {
        "über": "Klischee-Filter V2\nErkennt klischeehafte Bildmotive und verfolgt verschiedene Strategien, Klischees zu vermeiden\nV1: Direkte Inversion von Klischees. V2: Kontextuelle Neuinterpretation. V3: Kombination beider Ansätze mit verstärktem Negativprompt für maximale Klischee-Vermeidung.",
        "about": "Cliché Filter V2\nDetects clichéd image motifs and pursues different strategies to avoid clichés\nV1: Direct inversion of clichés. V2: Contextual reinterpretation. V3: Combination of both approaches with enhanced negative prompt for maximum cliché avoidance."
    },
    "ai4artsed_ClichéFilter_V3_250616192.json": {
        "über": "Klischee-Filter V3\nErkennt klischeehafte Bildmotive und verfolgt verschiedene Strategien, Klischees zu vermeiden\nV1: Direkte Inversion von Klischees. V2: Kontextuelle Neuinterpretation. V3: Kombination beider Ansätze mit verstärktem Negativprompt für maximale Klischee-Vermeidung.",
        "about": "Cliché Filter V3\nDetects clichéd image motifs and pursues different strategies to avoid clichés\nV1: Direct inversion of clichés. V2: Contextual reinterpretation. V3: Combination of both approaches with enhanced negative prompt for maximum cliché avoidance."
    },
    "ai4artsed_HunkyDoryHarmonizer_2507100933.json": {
        "über": "Harmonisierer\nNebenprodukt einer frühen Version des \"Kids-Safety\"-Filters\nVerniedlicht, versüßlicht, harmonisiert. Erzeugt bewusst übertrieben harmonische Bildkompositionen.",
        "about": "Harmonizer\nByproduct of an early version of the \"Kids-Safety\" filter\nCutifies, sweetens, harmonizes. Creates deliberately exaggerated harmonic image compositions."
    },
    "ai4artsed_Overdrive_2506152234.json": {
        "über": "Overdrive\nInspiriert vom gleichnamigen Gitarreneffekt\nTreibt visuelle Elemente an und über ihre Grenzen. Verstärkt Farben, Kontraste und Strukturen bis zur Verzerrung.",
        "about": "Overdrive\nInspired by the guitar effect of the same name\nDrives visual elements to and beyond their limits. Amplifies colors, contrasts and structures to the point of distortion."
    },
    
    # ARTS
    "ai4artsed_Dada_2506220140.json": {
        "über": "Dadaismus Transformation\nVersetzt sich in die Zeit und Situation dadaistischer Künstler_innen\nNutzt Absurdität, Zufall und Anti-Kunst-Prinzipien zur Transformation alltäglicher Prompts.",
        "about": "Dadaism Transformation\nPlaces itself in the time and situation of Dadaist artists\nUses absurdity, chance and anti-art principles to transform everyday prompts."
    },
    "ai4artsed_RandomArtisticStyle_2506121429.json": {
        "über": "Zufälliger Kunststil\nWählt jeweils eine aus 50 globalen Kunst- und kulturellen Ausdrucksformen als Vorlage\nEin experimenteller Workflow zur stilistischen Interpretation von Prompts.",
        "about": "Random Artistic Style\nSelects one of 50 global art and cultural forms of expression as template\nAn experimental workflow for stylistic interpretation of prompts."
    },
    "ai4artsed_TraditionalChinese_long_prompts_2506121345(1).json": {
        "über": "Traditionelle Chinesische Kunst\nInterpretiert Prompts nach visuellen Prinzipien einschließlich ihrer kosmologischen Hintergründe\nWendet Konzepte wie Leere, Yin-Yang und die fünf Elemente auf moderne Bildgenerierung an.",
        "about": "Traditional Chinese Art\nInterprets prompts according to visual principles including their cosmological backgrounds\nApplies concepts like emptiness, Yin-Yang and the five elements to modern image generation."
    },
    
    # FLOW
    "ai4artsed_ImageTextLoop_04_2506270855.json": {
        "über": "Bild-Text-Schleife (4 Iterationen)\nIterativer Prozess zwischen Bildbeschreibung und Bildgenerierung\nEin Bild wird beschrieben, die Beschreibung generiert ein neues Bild, welches wieder beschrieben wird. 4, 8 oder 16 Durchläufe.",
        "about": "Image-Text-Loop (4 iterations)\nIterative process between image description and image generation\nAn image is described, the description generates a new image, which is described again. 4, 8 or 16 cycles."
    },
    "ai4artsed_ImageTextLoop_08_2506270855.json": {
        "über": "Bild-Text-Schleife (8 Iterationen)\nIterativer Prozess zwischen Bildbeschreibung und Bildgenerierung\nEin Bild wird beschrieben, die Beschreibung generiert ein neues Bild, welches wieder beschrieben wird. 4, 8 oder 16 Durchläufe.",
        "about": "Image-Text-Loop (8 iterations)\nIterative process between image description and image generation\nAn image is described, the description generates a new image, which is described again. 4, 8 or 16 cycles."
    },
    "ai4artsed_ImageTextLoop_16_2506270855.json": {
        "über": "Bild-Text-Schleife (16 Iterationen)\nIterativer Prozess zwischen Bildbeschreibung und Bildgenerierung\nEin Bild wird beschrieben, die Beschreibung generiert ein neues Bild, welches wieder beschrieben wird. 4, 8 oder 16 Durchläufe.",
        "about": "Image-Text-Loop (16 iterations)\nIterative process between image description and image generation\nAn image is described, the description generates a new image, which is described again. 4, 8 or 16 cycles."
    },
    "ai4artsed_Inpainting_2507161820.json": {
        "über": "Inpainting\nFüllt ausgewählte Bildbereiche mit neuem Inhalt\nErmöglicht gezielte Bildbearbeitung durch Maskierung und Neugenerierung spezifischer Bereiche.",
        "about": "Inpainting\nFills selected image areas with new content\nEnables targeted image editing through masking and regeneration of specific areas."
    },
    "ai4artsed_OmniGen2ImageEdit_2507171341.json": {
        "über": "OmniGen2 Bildbearbeitung\nNutzt OmniGen2 für instruktionsbasierte Bildbearbeitung\nVersteht natürlichsprachliche Anweisungen zur Bildmanipulation ohne Maskierung.",
        "about": "OmniGen2 Image Editing\nUses OmniGen2 for instruction-based image editing\nUnderstands natural language instructions for image manipulation without masking."
    },
    "ai4artsed_Outpainting_2507170641.json": {
        "über": "Outpainting\nErweitert Bilder über ihre ursprünglichen Grenzen hinaus\nGeneriert kohärente Fortsetzungen bestehender Bilder in alle Richtungen. Version 2 mit verbesserter Randintegration.",
        "about": "Outpainting\nExtends images beyond their original boundaries\nGenerates coherent continuations of existing images in all directions. Version 2 with improved edge integration."
    },
    "ai4artsed_Outpainting2_2507170641.json": {
        "über": "Outpainting 2\nErweitert Bilder über ihre ursprünglichen Grenzen hinaus\nGeneriert kohärente Fortsetzungen bestehender Bilder in alle Richtungen. Version 2 mit verbesserter Randintegration.",
        "about": "Outpainting 2\nExtends images beyond their original boundaries\nGenerates coherent continuations of existing images in all directions. Version 2 with improved edge integration."
    },
    
    # MODEL
    "ai4artsed_(((PromptInterception)))_2507101853.json": {
        "über": "Prompt-Interception\nErmöglicht Erprobung von Prompt-Interception innerhalb eines Eingabefeldes\n(((Metaprompt in 3-fache Klammer setzen.))) Der Metaprompt transformiert den regulären Prompt vor der Bildgenerierung.",
        "about": "Prompt Interception\nEnables testing of prompt interception within an input field\n(((Put metaprompt in triple brackets.))) The metaprompt transforms the regular prompt before image generation."
    },
    "ai4artsed_Flux1dev-versus-StableDiffusion3.5_2507011342.json": {
        "über": "Flux1dev vs. Stable Diffusion 3.5 vs. MetaGen2\nVergleicht drei Bildgenerierungsmodelle direkt\nGeneriert dasselbe Motiv mit drei Modellen zur direkten Gegenüberstellung ihrer Charakteristika. (MetaGen2 wird noch ergänzt)",
        "about": "Flux1dev vs. Stable Diffusion 3.5 vs. MetaGen2\nDirectly compares three image generation models\nGenerates the same motif with three models for direct comparison of their characteristics. (MetaGen2 to be added)"
    },
    "ai4artsed_Stable-Diffusion_3.5_TellAStory_2507152203.json": {
        "über": "Stable Diffusion 3.5 - Geschichtenerzähler\nÜbersetzt Geschichten und Gedichte in Prompts\nErweitert auch kurze Prompts zu narrativen Bildkonzepten. Spezialisiert auf die Transformation literarischer Texte.",
        "about": "Stable Diffusion 3.5 - Tell A Story\nTranslates stories and poems into prompts\nAlso expands short prompts into narrative image concepts. Specialized in transforming literary texts."
    },
    "ai4artsed_Stable-Diffusion-3.5_2507152202.json": {
        "über": "Stable Diffusion 3.5 Standard\nBasis-Implementation des SD 3.5 Modells\nDirekter Zugang zum Stable Diffusion 3.5 Modell ohne zusätzliche Verarbeitungsschritte.",
        "about": "Stable Diffusion 3.5 Standard\nBasic implementation of the SD 3.5 model\nDirect access to the Stable Diffusion 3.5 model without additional processing steps."
    },
    
    # SEMANTICS
    "ai4artsed_Jugendsprache_2506122317.json": {
        "über": "Jugendsprache-Transformation\nÜbersetzt Prompts in aktuelle Jugendsprache\nTransformiert formelle oder neutrale Beschreibungen in die Ausdrucksweise zeitgenössischer Jugendkultur.",
        "about": "Youth Language Transformation\nTranslates prompts into current youth slang\nTransforms formal or neutral descriptions into the expression style of contemporary youth culture."
    },
    "ai4artsed_PigLatin_2506122317.json": {
        "über": "Pig Latin Transformation\nWendet Pig-Latin-Regeln auf Prompts an\nEin spielerischer linguistischer Filter, der Wörter nach Pig-Latin-Prinzipien umformt.",
        "about": "Pig Latin Transformation\nApplies Pig Latin rules to prompts\nA playful linguistic filter that transforms words according to Pig Latin principles."
    },
    "ai4artsed_StillePost_2506232347.json": {
        "über": "Stille Post\nSimuliert den Stille-Post-Effekt durch mehrfache Übersetzungen\nDer Prompt durchläuft mehrere Sprachen und kehrt verändert zurück. Übersetzungsfehler und -ungenauigkeiten der Sprachmodelle werden im Bildergebnis sichtbar. Eignet sich für Spiele (wie ist es zu dem Bild gekommen)?",
        "about": "Chinese Whispers\nSimulates the Chinese whispers effect through multiple translations\nThe prompt passes through several languages and returns changed. Translation errors and inaccuracies of language models become visible in the image result. Suitable for games (how did this image come about)?"
    },
    "ai4artsed_TheOpposite_2507122354.json": {
        "über": "Das Gegenteil\nKehrt die Bedeutung von Prompts ins Gegenteil um\nErsetzt semantische Elemente und auch ihre Beziehungen zueinander ins Gegenteil. Systematische Inversion von Konzepten.",
        "about": "The Opposite\nReverses the meaning of prompts to their opposite\nReplaces semantic elements and also their relationships to each other with opposites. Systematic inversion of concepts."
    },
    
    # SOUND
    "ai4artsed_MusicGen_simple_2506211630.json": {
        "über": "MusicGen Einfach\nBasis-Musikgenerierung mit MusicGen\nWandelt Textbeschreibungen in Musikstücke um. Einfache, direkte Anwendung des MusicGen-Modells.",
        "about": "MusicGen Simple\nBasic music generation with MusicGen\nConverts text descriptions into music pieces. Simple, direct application of the MusicGen model."
    },
    "ai4artsed_StableAudio_2506291524.json": {
        "über": "Stable Audio Standard\nAudiogenerierung mit Stable Audio (auch für AceStep vorbereitet)\nErzeugt Klänge, Geräusche und kurze Musikstücke aus Textbeschreibungen. Unterstützt verschiedene Audio-Backends.",
        "about": "Stable Audio Standard\nAudio generation with Stable Audio (also prepared for AceStep)\nCreates sounds, noises and short music pieces from text descriptions. Supports various audio backends."
    },
    "ai4artsed_StableAudio_TellAStory_2506291505.json": {
        "über": "Stable Audio - Geschichtenerzähler\nNarrative Audiogenerierung (auch für AceStep vorbereitet)\nOptimiert für die Erzeugung von Klanglandschaften, die Geschichten unterstützen oder erzählen. Unterstützt verschiedene Audio-Backends.",
        "about": "Stable Audio - Tell A Story\nNarrative audio generation (also prepared for AceStep)\nOptimized for creating soundscapes that support or tell stories. Supports various audio backends."
    },
    
    # VECTOR
    "ai4artsed_SplitAndCombineLinear_2507021805.json": {
        "über": "Lineare Vektoraufteilung\nMathematische Dekonstruktion von Bedeutungsräumen, lineare Variante\nZerlegt Prompts in Vektorkomponenten und sucht den direkten (linearen) Weg zwischen den Punkten im latenten Bedeutungsraum. Ergebnisse können überraschen oder auch konventionell ausfallen.",
        "about": "Linear Vector Split\nMathematical deconstruction of meaning spaces, linear variant\nBreaks down prompts into vector components and finds the direct (linear) path between points in latent meaning space. Results can be surprising or conventional."
    },
    "ai4artsed_SplitAndCombineSpherical_2507021805.json": {
        "über": "Sphärische Vektoraufteilung\nMathematische Dekonstruktion von Bedeutungsräumen, sphärische Variante\nZerlegt Prompts in Vektorkomponenten und sucht kurvige Wege zwischen den Punkten im latenten Bedeutungsraum. Tendiert zu organischeren, weniger vorhersehbaren Ergebnissen.",
        "about": "Spherical Vector Split\nMathematical deconstruction of meaning spaces, spherical variant\nBreaks down prompts into vector components and finds curved paths between points in latent meaning space. Tends towards more organic, less predictable results."
    },
    "ai4artsed_Surrealization_2506092253.json": {
        "über": "Surrealisierung\nVerschiebt Prompts in surreale Dimensionen\nNutzt Vektormanipulation um realistische Konzepte systematisch zu verfremden.",
        "about": "Surrealization\nShifts prompts into surreal dimensions\nUses vector manipulation to systematically alienate realistic concepts."
    },
    "ai4artsed_YesAndNo_V1_2506271433.json": {
        "über": "Ja und Nein V1\nErzeugt gegensätzliche Interpretationen desselben Prompts\nV1: Binäre Opposition durch Antonymersetzung. V2: Dialektische Synthese - sucht nach der Vereinigung der Gegensätze in einem Bild. Exploration von Ambivalenz und Dualität.",
        "about": "Yes and No V1\nCreates opposing interpretations of the same prompt\nV1: Binary opposition through antonym replacement. V2: Dialectical synthesis - seeks unification of opposites in one image. Exploration of ambivalence and duality."
    },
    "ai4artsed_YesAndNo_V2_2506271433.json": {
        "über": "Ja und Nein V2\nErzeugt gegensätzliche Interpretationen desselben Prompts\nV1: Binäre Opposition durch Antonymersetzung. V2: Dialektische Synthese - sucht nach der Vereinigung der Gegensätze in einem Bild. Exploration von Ambivalenz und Dualität.",
        "about": "Yes and No V2\nCreates opposing interpretations of the same prompt\nV1: Binary opposition through antonym replacement. V2: Dialectical synthesis - seeks unification of opposites in one image. Exploration of ambivalence and duality."
    }
}

def add_about_nodes(workflow_path: Path, über_text: str, about_text: str):
    """Add über and about nodes to a workflow file"""
    
    # Read workflow
    with open(workflow_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)
    
    # Find highest node ID
    max_id = max(int(node_id) for node_id in workflow.keys())
    
    # Add nodes with new IDs
    über_id = str(max_id + 1)
    about_id = str(max_id + 2)
    
    # Create nodes
    workflow[über_id] = {
        "inputs": {
            "value": über_text
        },
        "class_type": "PrimitiveStringMultiline",
        "_meta": {
            "title": "über"
        }
    }
    
    workflow[about_id] = {
        "inputs": {
            "value": about_text
        },
        "class_type": "PrimitiveStringMultiline",
        "_meta": {
            "title": "about"
        }
    }
    
    # Write back
    with open(workflow_path, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, ensure_ascii=False, indent=2)
    
    print(f"Added nodes {über_id} (über) and {about_id} (about) to {workflow_path.name}")

def main():
    # Base directory for workflows
    workflows_dir = Path("../workflows")
    
    # Process each workflow
    success_count = 0
    error_count = 0
    
    for filename, texts in workflow_texts.items():
        # Find the file in subdirectories
        found = False
        for workflow_path in workflows_dir.rglob(filename):
            if workflow_path.is_file():
                try:
                    add_about_nodes(workflow_path, texts["über"], texts["about"])
                    success_count += 1
                    found = True
                    break
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
                    error_count += 1
                    found = True
                    break
        
        if not found:
            print(f"Warning: {filename} not found in workflow directories")
            error_count += 1
    
    print(f"\nCompleted: {success_count} workflows updated successfully, {error_count} errors")

if __name__ == "__main__":
    main()
