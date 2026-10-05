import { FormEvent, useEffect, useRef, useState } from "react";
import { Link, matchPath, useLocation } from "react-router-dom";
import { getChatHistory, sendChatMessage } from "../api";
import { useAuth } from "../auth";
import type { ChatHistoryMessage, ChatProduct } from "../types";

interface Message extends ChatHistoryMessage {
  products?: ChatProduct[];
}

interface ChatWidgetProps {
  onProducts: (products: ChatProduct[]) => void;
}

const welcome: Message = {
  role: "assistant",
  content: "Hi! I’m your Campus Customs concierge. Tell me what you’re shopping for, and I’ll look through the collection.",
};

export function ChatWidget({ onProducts }: ChatWidgetProps) {
  const { user, loading: authLoading } = useAuth();
  const location = useLocation();
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const [failedMessage, setFailedMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([welcome]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      setMessages([welcome]);
      return;
    }
    getChatHistory()
      .then(({ messages: saved }) => {
        const restored: Message[] = saved.map(({ role, content, products }) => ({
          role,
          content,
          products,
        }));
        setMessages(restored.length > 0 ? [welcome, ...restored] : [welcome]);
        const lastProducts = [...restored].reverse().find((item) => item.products?.length)?.products;
        if (lastProducts) onProducts(lastProducts);
      })
      .catch(() => {
        setMessages([welcome]);
        setError("Your saved conversation could not be loaded. You can still start a new chat.");
      });
  }, [authLoading, onProducts, user]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, sending]);

  const submitMessage = async (text: string, displayUserMessage = true) => {
    if (!text || sending) return;

    setError("");
    setFailedMessage("");
    const last = messages[messages.length - 1];
    const historySource = !displayUserMessage && last?.role === "user" && last.content === text
      ? messages.slice(0, -1)
      : messages;
    const history = historySource.map(({ role, content }) => ({ role, content }));
    if (displayUserMessage) {
      setMessages((current) => [...current, { role: "user", content: text }]);
    }
    setDraft("");
    setSending(true);

    try {
      const productMatch = matchPath("/products/:productId", location.pathname);
      const result = await sendChatMessage(text, history, {
        path: location.pathname,
        ...(productMatch?.params.productId
          ? { product_id: productMatch.params.productId }
          : {}),
      });
      if (result.products.length > 0) onProducts(result.products);
      const responseText = result.follow_up_question && !result.reply.includes(result.follow_up_question)
        ? `${result.reply}\n\n${result.follow_up_question}`
        : result.reply;
      setMessages((current) => [
        ...current,
        { role: "assistant", content: responseText, products: result.products },
      ]);
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "I’m having trouble connecting right now. Please try again.",
      );
      setFailedMessage(text);
    } finally {
      setSending(false);
    }
  };

  const send = (event: FormEvent) => {
    event.preventDefault();
    void submitMessage(draft.trim());
  };

  const retry = () => {
    if (!failedMessage) return;
    void submitMessage(failedMessage, false);
  };

  return (
    <aside className={`chat-widget ${open ? "open" : ""}`} aria-label="Campus Customs chat">
      {open && (
        <div className="chat-panel">
          <div className="chat-header">
            <span className="chat-brand-mark" aria-hidden="true">୨୧</span>
            <div>
              <span className="chat-status" />
              <strong>Ask Campus Customs</strong>
              <small>{sending ? "Searching the shop…" : error ? "Connection needs attention" : "Ready to help"}</small>
            </div>
            <button type="button" onClick={() => setOpen(false)} aria-label="Close chat">×</button>
          </div>
          <div className="chat-messages" ref={scrollRef} aria-live="polite" aria-busy={sending}>
            {messages.map((message, index) => (
              <div key={`${message.role}-${index}`} className={`chat-entry ${message.role}`}>
                <p className={`chat-message ${message.role}`}>{message.content}</p>
                {message.products && message.products.length > 0 && (
                  <div className="chat-products">
                    {message.products.map((product) => (
                      <Link
                        key={product.product_id}
                        to={`/products/${product.product_id}`}
                        onClick={() => setOpen(false)}
                      >
                        <img src={product.image_url} alt="" />
                        <span><strong>{product.name}</strong><small>${product.price.toFixed(2)}</small></span>
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {messages.length === 1 && !sending && !error && (
              <div className="chat-starters" aria-label="Suggested questions">
                {["Show me Yale hoodies", "Gifts for a Yale dad", "What’s available in medium?"].map((prompt) => (
                  <button key={prompt} type="button" onClick={() => void submitMessage(prompt)}>
                    {prompt}
                  </button>
                ))}
              </div>
            )}
            {sending && (
              <div className="chat-loading" role="status">
                <p className="chat-message assistant typing" aria-label="Assistant is responding"><i /><i /><i /></p>
                <span>Checking the catalogue…</span>
              </div>
            )}
            {error && (
              <div className="chat-error" role="alert">
                <strong>Couldn’t get a reply</strong>
                <span>{error}</span>
                {failedMessage && <button type="button" onClick={retry}>Try again</button>}
              </div>
            )}
          </div>
          <form className="chat-form" onSubmit={send}>
            <input
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Ask about a product…"
              aria-label="Chat message"
              maxLength={2000}
              disabled={sending}
            />
            <button type="submit" aria-label="Send message" disabled={sending || !draft.trim()}>→</button>
          </form>
        </div>
      )}
      <button
        className="chat-launcher"
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
      >
        <span aria-hidden="true">{open ? "×" : "୨୧"}</span>
        <span className="chat-launcher-label">{open ? "Close" : "Ask us"}</span>
      </button>
    </aside>
  );
}
