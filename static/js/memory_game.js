/* static/js/memory_game.js 
    音神経衰弱ゲームを制御するスクリプト
*/

document.addEventListener('DOMContentLoaded', () => {
    // ゲームボード、タイマー、ベストタイム、サウンドプレイヤー、ボタンの要素を取得
    const gameBoard = document.getElementById('game-board');
    const timerElement = document.getElementById('timer');
    const bestTimeElement = document.getElementById('best-time');
    const soundPlayer = document.getElementById('sound-player');
    const startButton = document.getElementById('start-button');
    const restartButton = document.getElementById('restart-button');

    // カードの種類と対応する音声ファイルを定義
    const cardTypes = [
        { type: 'plastic_bottle', sound: 'plastic_bottle.mp3' },
        { type: 'steel_can', sound: 'steel_can.mp3' },
        { type: 'aluminum_can', sound: 'aluminum_can.mp3' },
        { type: 'spray_can', sound: 'spray_can.mp3' },
        { type: 'container_with_contents', sound: 'container_with_contents.mp3' }
    ];

    // カードの配列を初期化
    let cards = [];
    cardTypes.forEach(({ type, sound }) => {
        // 各カードを2つ作成(ペアの作成)
        cards.push({ type, sound }, { type, sound });
    });

    /* ゲームの状態を管理する関数 */
    let firstCard, secondCard;
    let lockBoard = false;  // カードの操作を制御するフラグ
    let matchedPairs = 0;   // マッチしたペアの数
    let gameStarted = false; //  ゲームの開始状態
    let startTime, timerInterval;  // ゲーム開始時間とタイマーのインターバル

     // 保存されたベストタイムを取得し表示
    const bestTime = localStorage.getItem('bestTime');
    bestTimeElement.textContent = bestTime ? bestTime : '00:00';

     /* 配列をシャッフルする関数 */
    function shuffle(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];  // 要素の入れ替え
        }
        return array;
    }

    /* カードを作成する関数 */
    function createCard(type, sound) {
        const card = document.createElement('div');
        card.classList.add('card');
        card.dataset.type = type;  // カードの種類をデータ属性で保存
        card.dataset.sound = sound;  // サウンドファイルをデータ属性で保存

         // 裏面の青色のカードを最初に表示
        const imgBack = document.createElement('img');
        imgBack.src = 'static/images/card_back_blue.png'; 
        imgBack.classList.add('card-image');
        card.appendChild(imgBack);

         // 表面の画像を設定
        const imgFront = document.createElement('img');
        imgFront.src = ''; 
        imgFront.classList.add('card-image');
        card.appendChild(imgFront);

        card.addEventListener('click', flipCard);  // カードのクリックイベントを追加
        return card;
    }

     /* ボードをセットアップする関数 */
    function setupBoard() {
        const shuffledCards = shuffle(cards);  // カードをシャッフル
        gameBoard.innerHTML = '';  // ボードをクリア
        shuffledCards.forEach(({ type, sound }) => {
            gameBoard.appendChild(createCard(type, sound));  // カードをボードに追加
        });
    }

    /* ゲームを開始する関数 */
    function startGame() {
        matchedPairs = 0;  // マッチしたペア数をリセット
        gameStarted = true;  // ゲーム開始フラグを設定
        startTime = Date.now();  // 開始時間を記録
        timerInterval = setInterval(updateTimer, 1000);  // タイマーを開始
        setupBoard();  // ボードをセットアップ
        startButton.style.display = 'none';  // 開始ボタンを非表示
        restartButton.style.display = 'none';  // 再スタートボタンを非表示
    }

     /* ゲームを再スタートする関数 */
    function restartGame() {
        matchedPairs = 0; 
        gameStarted = true; 
        startTime = Date.now(); 
        timerInterval = setInterval(updateTimer, 1000); 
        setupBoard(); 
        restartButton.style.display = 'none'; 
    }

     /* カードをめくる関数 */
    function flipCard() {
        // 既にめくっている場合は処理を中止
        if (lockBoard || this === firstCard || this.classList.contains('matched')) return; 

        this.classList.add('flipped');  // カードをめくる
        const imgBack = this.querySelector('img:nth-child(1)');
        imgBack.src = 'static/images/card_back_white.png'; // めくった後の白色のカードを表示 

        soundPlayer.src = `static/sounds/${this.dataset.sound}`;  // サウンドを設定
        soundPlayer.play();  // サウンドを再生

        if (!firstCard) {
            firstCard = this;  // 最初のカードを記録
            return;
        }

        secondCard = this;  // 2番目のカードを記録
        lockBoard = true;  // ボードをロック
        checkMatch();  // ペアが揃っているかチェック
    }

    /* ペアの一致をチェックする関数 */
    function checkMatch() {
        const isMatch = firstCard.dataset.sound === secondCard.dataset.sound;  // 音声が一致するかどうか

        if (isMatch) {
            matchedPairs += 1;  // マッチしたペア数を加算
            setTimeout(() => {
                // 正解時のアニメーションクラスを追加
                firstCard.classList.add('matched'); 
                secondCard.classList.add('matched'); 
                // 正解時にゴミの種類の画像を表示
                firstCard.querySelector('.card-image').src = `static/images/${firstCard.dataset.type}.png`; 
                secondCard.querySelector('.card-image').src = `static/images/${secondCard.dataset.type}.png`; 
                resetBoard();  // ボードをリセット

                 // 全てのペアが見つかった場合、ゲームを終了
                if (matchedPairs === 5) {
                    endGame();
                }
            }, 1000);
        } else {
            setTimeout(() => {
                 // カードをひっくり返す
                firstCard.classList.remove('flipped'); 
                secondCard.classList.remove('flipped'); 
                 // 裏面の青いカードに戻す
                firstCard.querySelector('.card-image').src = 'static/images/card_back_blue.png'; 
                secondCard.querySelector('.card-image').src = 'static/images/card_back_blue.png'; 
                resetBoard(); 
            }, 1000);
        }
    }

     /* ゲームを終了する関数 */
    function endGame() {
        clearInterval(timerInterval);  // タイマーを停止
        const elapsedTime = Math.floor((Date.now() - startTime) / 1000);  // 経過時間を計算
        const formattedTime = formatTime(elapsedTime); 

         // ベストタイムの更新
        const currentBestTime = localStorage.getItem('bestTime');
        if (!currentBestTime || elapsedTime < parseTime(currentBestTime)) {
            localStorage.setItem('bestTime', formattedTime);  // 新しいベストタイムを保存
            bestTimeElement.textContent = formattedTime;  // ベストタイムを表示
        }
        restartButton.style.display = 'block';  // 再スタートボタンを表示
    }

     /* ボードをリセットする関数 */
    function resetBoard() {
        [firstCard, secondCard] = [null, null];  // 最初のカードと2番目のカードをリセット
        lockBoard = false;  // ボードのロックを解除
    }

     /* タイマーを更新する関数 */
    function updateTimer() {
        const elapsedTime = Math.floor((Date.now() - startTime) / 1000);  // 経過時間を計算
        timerElement.textContent = formatTime(elapsedTime);  // 00:00形式で表示
    }

    /* 経過時間の形式を設定する関数 */
    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);  // 分を計算
        const remainingSeconds = seconds % 60;  // 秒を計算
        return `${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;  // 00:00形式
    }

    /* 保存されたベストタイムを数値として取得する関数 */
    function parseTime(timeString) {
        const [minutes, seconds] = timeString.split(':').map(Number);  // 分と秒を取得
        return minutes * 60 + seconds;  // 総秒数を返す
    }

     // ボタンのイベントリスナーを設定
    startButton.addEventListener('click', startGame);  // 開始ボタン
    restartButton.addEventListener('click', restartGame);  // 再スタートボタン
});
