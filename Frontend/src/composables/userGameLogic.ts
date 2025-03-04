import { ref, computed } from 'vue';
import type { GameSettings } from '@/types/gametypes';

export function useGameLogic(settings: GameSettings) {
  const target = ref(0);
  const addends = ref<number[]>([]);
  const tiltAngle = ref(0);
  const isBalanced = ref(false);

  const currentSum = computed(() => {
    return addends.value.reduce((sum, num) => sum + (num || 0), 0);
  });

  function generateTarget() {
    const { minTarget, maxTarget } = settings;
    target.value = Math.floor(Math.random() * (maxTarget - minTarget + 1)) + minTarget;
  }

  function calculateTilt() {
    const sum = currentSum.value;
    if (sum === target.value) {
      tiltAngle.value = 0;
      isBalanced.value = true;
    } else if (sum < target.value) {
      tiltAngle.value = -15 * (1 - sum/target.value);
      isBalanced.value = false;
    } else {
      tiltAngle.value = 15 * (sum/target.value - 1);
      isBalanced.value = false;
    }
  }

  return {
    target,
    addends,
    tiltAngle,
    isBalanced,
    currentSum,
    generateTarget,
    calculateTilt
  };
}

