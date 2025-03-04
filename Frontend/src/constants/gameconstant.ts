import { GameSettings } from "@/types/gametypes"

export const DIFFICULTY_RANGES = {
    easy: {min: 1, max: 10},
    medium: {min: 1, max: 20},
    hard: {min: 1, max: 50}
}

export const DEFAULT_SETTING: GameSettings = {
    difficulty: "easy",
    numberofAddends: 2,
    minTarget: 5,
    maxTarget: 20
}

