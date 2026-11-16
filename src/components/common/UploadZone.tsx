import React, { useRef, useState } from 'react';
import { UploadCloud, Image as ImageIcon, X, RefreshCw, Camera, AlertCircle } from 'lucide-react';

interface UploadZoneProps {
  onImageSelected: (file: File | string, previewUrl: string) => void;
  selectedPreview?: string;
  onClear?: () => void;
  acceptedFormats?: string[];
  maxSizeMb?: number;
  label?: string;
  subLabel?: string;
}

export const UploadZone: React.FC<UploadZoneProps> = ({
  onImageSelected,
  selectedPreview,
  onClear,
  acceptedFormats = ['image/jpeg', 'image/png', 'image/jpg'],
  maxSizeMb = 10,
  label = 'Upload leaf or crop photograph for AI disease analysis',
  subLabel = 'Drag & drop image here or browse from device (JPG, PNG up to 10MB)',
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const processFile = (file: File) => {
    setError(null);
    if (!acceptedFormats.includes(file.type)) {
      setError('Please upload a valid image file (JPG, JPEG, or PNG).');
      return;
    }
    if (file.size > maxSizeMb * 1024 * 1024) {
      setError(`File size exceeds ${maxSizeMb}MB. Please select a smaller photo.`);
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const result = e.target?.result as string;
      onImageSelected(file, result);
    };
    reader.readAsDataURL(file);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  return (
    <div className="w-full">
      {/* Hidden inputs */}
      <input
        ref={fileInputRef}
        type="file"
        accept={acceptedFormats.join(',')}
        onChange={handleFileChange}
        className="hidden"
      />
      <input
        ref={cameraInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        onChange={handleFileChange}
        className="hidden"
      />

      {selectedPreview ? (
        <div className="relative rounded-2xl overflow-hidden border-2 border-forest-500/40 bg-charcoal-900 shadow-soft-lg group">
          <img
            src={selectedPreview}
            alt="Leaf Preview"
            className="w-full h-72 sm:h-80 object-cover"
          />

          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent flex flex-col justify-between p-4">
            <div className="flex items-center justify-between">
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-forest-900/90 text-white backdrop-blur-md border border-forest-500/30 flex items-center gap-1.5">
                <ImageIcon className="w-3.5 h-3.5 text-saffron-400" />
                Image Loaded for Vision Inference
              </span>

              <button
                type="button"
                onClick={onClear}
                className="p-2 rounded-full bg-black/60 hover:bg-rose-600 text-white transition-all backdrop-blur-md"
                title="Remove image"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="flex items-center justify-end gap-2">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-white/90 hover:bg-white text-forest-900 flex items-center gap-1.5 shadow-md transition-all backdrop-blur-md"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Replace Image
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`cursor-pointer rounded-2xl border-2 border-dashed p-8 sm:p-10 text-center transition-all duration-200 ${
            isDragging
              ? 'border-forest-600 bg-forest-50/70 scale-[0.99]'
              : 'border-forest-200 hover:border-forest-400 bg-white hover:bg-forest-50/20'
          }`}
        >
          <div className="mx-auto w-16 h-16 rounded-2xl bg-forest-50 border border-forest-100 flex items-center justify-center text-forest-700 shadow-sm mb-4">
            <UploadCloud className="w-8 h-8" />
          </div>

          <h4 className="text-base font-bold text-forest-900">{label}</h4>
          <p className="mt-1 text-xs text-charcoal-400 max-w-sm mx-auto">{subLabel}</p>

          <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                fileInputRef.current?.click();
              }}
              className="px-4 py-2 rounded-xl text-xs font-bold bg-forest-900 hover:bg-forest-800 text-white shadow-sm transition-all"
            >
              Browse Files
            </button>

            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                cameraInputRef.current?.click();
              }}
              className="px-4 py-2 rounded-xl text-xs font-bold bg-saffron-50 hover:bg-saffron-100 text-saffron-900 border border-saffron-300 flex items-center gap-1.5 shadow-sm transition-all"
            >
              <Camera className="w-3.5 h-3.5" />
              Capture via Camera
            </button>
          </div>
        </div>
      )}

      {error && (
        <div className="mt-3 p-3 rounded-xl bg-rose-50 border border-rose-200 flex items-center gap-2 text-xs text-rose-700 font-medium">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};
