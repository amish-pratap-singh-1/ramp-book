import Modal from "./Modal";

interface ConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  isDestructive?: boolean;
  isLoading?: boolean;
}

export default function ConfirmModal({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  isDestructive = true,
  isLoading = false,
}: ConfirmModalProps) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title}>
      <p className="text-secondary mb-8 leading-relaxed">
        {message}
      </p>
      <div className="flex gap-3 justify-end">
        <button onClick={onClose} className="btn-ghost" disabled={isLoading}>
          {cancelLabel}
        </button>
        <button 
          onClick={onConfirm} 
          disabled={isLoading}
          className={isDestructive ? "btn-danger" : "btn-primary"}
        >
          {isLoading ? "Processing..." : confirmLabel}
        </button>
      </div>
    </Modal>
  );
}
