import { computed, Ref } from 'vue';

export function useFeedback(currentSum: Ref<number>, target: Ref<number>, isBalanced: Ref<boolean>) {
  const feedbackMessage = computed(() => {
    if (currentSum.value === 0) return 'Add numbers to balance the scale!';
    if (isBalanced.value) return 'Perfect balance! Well done!';
    if (currentSum.value < target.value) return 'Add more to balance the scale!';
    return 'Too heavy! Try smaller numbers!';
  });

  const feedbackClass = computed(() => ({
    'bg-blue-100 text-blue-700': currentSum.value === 0,
    'bg-yellow-100 text-yellow-700': currentSum.value < target.value && currentSum.value !== 0,
    'bg-red-100 text-red-700': currentSum.value > target.value,
    'bg-green-100 text-green-700': isBalanced.value
  }));

  return {
    feedbackMessage,
    feedbackClass
  };
}
