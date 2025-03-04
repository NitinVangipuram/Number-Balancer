export interface GameSettings {
    difficulty: "easy" | "medium" | "hard";
    numberofAddends: number;
    minTarget: number;
    maxTarget: number;
}

export interface GameState{
    target: number;
    addends: number[];
    isCorrect: boolean;
}
