@@
 async def ent_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
-    text = update.effective_message.text
-    print(f"[TRACE] ent:ent_button_handler | text: {text}")
+    text = update.effective_message.text
+    # use repr to show invisible characters in logs
+    print(f"[TRACE] ent:ent_button_handler | text: {repr(text)}")
@@
-    elif text == "🎮 بازی‌ها":
-        from bot.utils.keyboards import get_games_menu
-        await update.effective_message.reply_text("🎮 به بخش بازی‌های سکتور خوش اومدی!\nیکی رو انتخاب کن و شروع کنیم:", reply_markup=get_games_m[...]
+    elif text == "🎮 بازی‌ها":
+        from bot.utils.keyboards import get_games_menu
+        # Protective logging: print before sending, and catch any exception to log it.
+        try:
+            print("[TRACE] ent:ent_button_handler | sending games menu")
+            await update.effective_message.reply_text(
+                "🎮 به بخش بازی‌های سکتور خوش اومدی!\nیکی رو انتخاب کن و شروع کنیم:",
+                reply_markup=get_games_menu()
+            )
+        except Exception as e:
+            print(f"[ERROR] ent:ent_button_handler | exception while sending games menu: {e}", flush=True)
+            raise
@@
     print(f"[TRACE] ent:ent_button_handler | handled | ApplicationHandlerStop")
     raise ApplicationHandlerStop()
