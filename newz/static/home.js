
const resetButton = document.querySelector('.reset-all-button');
const resetTooltip = resetButton.querySelector('.reset-all-button__tooltip');

const getButton = document.querySelector('.get-new');
const getTooltip = getButton.querySelector('.get-new__tooltip');

const statisticButton = document.querySelector('.statistic');
const statisticTooltip = statisticButton.querySelector('.statistic__tooltip');

document.addEventListener('mousemove', evt => {
  const x = evt.clientX / innerWidth;
  const y = evt.clientY / innerHeight;

  resetButton.style.setProperty('--mouse-x', `${x * 100}%`);
  resetButton.style.setProperty('--mouse-y', `${y * 100}%`);

  resetTooltip.style.left = `${evt.pageX + 5}px`;
  resetTooltip.style.top = `${evt.pageY - resetTooltip.offsetHeight - 5}px`;

  getButton.style.setProperty('--mouse-x', `${x * 100}%`);
  getButton.style.setProperty('--mouse-y', `${y * 100}%`);

  getTooltip.style.left = `${evt.pageX + 5}px`;
  getTooltip.style.top = `${evt.pageY - getTooltip.offsetHeight - 5}px`;

  statisticButton.style.setProperty('--mouse-x', `${x * 100}%`);
  statisticButton.style.setProperty('--mouse-y', `${y * 100}%`);

  statisticTooltip.style.left = `${evt.pageX + 5}px`;
  statisticTooltip.style.top = `${evt.pageY - statisticTooltip.offsetHeight - 5}px`;
});

const activateLoader = () => {
    const loader = document.getElementById('loader')
    loader.style.display = 'flex'
}