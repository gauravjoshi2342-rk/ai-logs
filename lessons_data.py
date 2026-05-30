# lessons_data.py

LESSONS = [
    {
        "id": "bunny_face",
        "title": "Cute Cartoon Bunny",
        "category": "Animals",
        "level": "Beginner",
        "xp_reward": 150,
        "steps": [
            {
                "step_num": 1,
                "instruction": "Step 1: Draw a perfect smooth circle for the head guide.",
                "shape_type": "circle",
                "coords": [100, 100, 300, 300]  # [x1, y1, x2, y2]
            },
            {
                "step_num": 2,
                "instruction": "Step 2: Add two long vertical oval ears on top of the head.",
                "shape_type": "ears",
                "coords": [(120, 20, 180, 110), (220, 20, 280, 110)]
            },
            {
                "step_num": 3,
                "instruction": "Step 3: Sketch the eyes and an arching happy smile!",
                "shape_type": "face_features",
                "coords": [(150, 180), (250, 180), (160, 220, 240, 250)]
            }
        ]
    }
]
