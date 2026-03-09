# SoChi BLOCKS — 公開手順

> 友達にシェアするための2つの方法。**Vercel が圧倒的に楽**なのでまずこちらを推奨。

---

## 前提: GitHub に最新コードを push する

```bash
# プロジェクトルートで
git add .
git commit -m "feat: publish SoChi BLOCKS"
git push origin master
```

---

## 方法 A — Vercel（推奨・5分で完了）

ゼロ設定。Next.js の作者が作ったサービスなので相性が一番良い。
無料プランで十分。`master` push のたびに**自動デプロイ**される。

### 手順

1. **[vercel.com](https://vercel.com) にアクセス**
   - 「Sign Up」→「Continue with GitHub」でログイン

2. **プロジェクトをインポート**
   - 「Add New… → Project」
   - `Souchi-lab/3d-sudoku` を選択 → 「Import」

3. **ルートディレクトリを指定**
   - `Root Directory` 欄に **`web-app`** と入力
   - （他の設定はそのままでOK）

4. **「Deploy」をクリック**
   - 1〜2分で完了

5. **URLが発行される**
   - 例: `https://3d-sudoku.vercel.app`
   - このURLを友達に送るだけ！

### Tips
- Vercel のダッシュボードで**カスタムドメイン**も無料で設定できる
- 毎回の `git push` で自動更新されるので再デプロイ操作は不要
- デプロイごとに**プレビューURL**が発行されるので、変更を見せてからマージもできる

---

## 方法 B — GitHub Pages（完全無料・自動化済み）

`.github/workflows/deploy-pages.yml` が用意済み。
`master` に push するだけで自動ビルド・デプロイされる。

### 初回のみ必要な設定

1. **GitHub リポジトリを開く**
   - [github.com/Souchi-lab/3d-sudoku](https://github.com/Souchi-lab/3d-sudoku)

2. **Pages を有効化**
   - `Settings` → `Pages`
   - `Source` を **`GitHub Actions`** に変更 → 「Save」

3. **`master` に push する**（前提の手順を実行済みならOK）
   - Actions タブで進捗を確認できる

4. **URLにアクセス**
   - `https://souchi-lab.github.io/3d-sudoku/`

### Tips
- Vercel より反映が少し遅い（2〜3分）
- GitHub アカウントさえあれば完全無料
- Actions タブの「Run workflow」で手動デプロイも可能

---

## 友達へのシェア方法

### URLを送る
```
SoChi BLOCKSというゲーム作ったから遊んでみて！
👉 https://3d-sudoku.vercel.app
3Dキューブで解くナンプレです。PC推奨！
```

### フィードバックをもらう際のお願い文（コピペ用）
```
遊んでみての感想を教えてください！
- 操作方法はわかりやすかった？（1〜5点）
- どの難易度で詰まった？
- 「これがあったら嬉しい」機能は？
- バグや不具合があれば教えてください
```

---

## ローカルで動作確認

```bash
cd web-app
npm run dev      # http://localhost:3000 でプレイ
npm test         # テスト実行（48テスト）
npm run build    # 本番ビルド確認
```

---

## トラブルシューティング

| 症状 | 対処 |
|------|------|
| Vercel ビルドが失敗する | Root Directory が `web-app` になっているか確認 |
| GitHub Pages が 404 | Settings → Pages → Source が `GitHub Actions` になっているか確認 |
| 画面が真っ白 | ブラウザのキャッシュをクリア（Ctrl+Shift+R）|
| 3Dキューブが表示されない | WebGL 対応ブラウザ（Chrome / Firefox / Edge）を使用 |
