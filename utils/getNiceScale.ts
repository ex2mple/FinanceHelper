export function calculateNiceScale(minValue: number, maxValue: number, desiredTicks = 6) {
  const range = maxValue - minValue;

  // Обработка случая, когда диапазон некорректен или нулевой
  if (range <= 0 || !isFinite(range)) {
    // Возвращаем стандартные значения или обрабатываем ошибку
    const defaultStep = 1;
    return {
      stepSize: defaultStep,
      axisMin: Math.floor(minValue), // Просто округляем
      axisMax: Math.ceil(maxValue) || defaultStep, // Округляем или ставим шаг
    };
  }

  const roughStep = range / desiredTicks;
  const magnitude = Math.pow(10, Math.floor(Math.log10(roughStep)));
  const normalizedStep = roughStep / magnitude;

  let niceNormalizedStep;
  if (normalizedStep <= 1) {
    niceNormalizedStep = 1;
  } else if (normalizedStep <= 2) {
    niceNormalizedStep = 2;
  } else if (normalizedStep <= 5) {
    niceNormalizedStep = 5;
  } else {
    niceNormalizedStep = 10;
  }

  const niceStep = niceNormalizedStep * magnitude;

  // Рассчитываем "красивые" границы оси
  const axisMin = Math.floor(minValue / niceStep) * niceStep;
  const axisMax = Math.ceil(maxValue / niceStep) * niceStep;

   // Предотвращаем бесконечный цикл, если maxValue очень мал и axisMax становится 0
   if (axisMax === axisMin && axisMax === 0 && maxValue > 0) {
      // Если максимум был положительный, но округлился до 0,
      // ставим верхнюю границу равной шагу
      return {
          stepSize: niceStep,
          axisMin: 0,
          axisMax: niceStep
      };
   }

  return {
    stepSize: niceStep,
    axisMin: axisMin,
    axisMax: axisMax, // Это можно использовать для опции 'max' в Chart.js
  };
}