import tensorflow as tf
from transformers import TFBertModel, BertTokenizer
from tensorflow.keras import layers, initializers, optimizers, callbacks

model_name = "bert-base-uncased"
tokenizer = BertTokenizer.from_pretrained(model_name)
bert_model = TFBertModel.from_pretrained(model_name)
NUM_FEATURES = 9  # Define the number of numerical features if not provided elsewhere

print("TensorFlow version:", tf.__version__)
print("Is GPU available:", tf.test.is_gpu_available())

def build_model(NUM_FEATURES=NUM_FEATURES):
    input_ids = layers.Input(shape=(128,), dtype=tf.int32, name="input_ids")
    attention_mask = layers.Input(shape=(128,), dtype=tf.int32, name="attention_mask")
    numerical_features = layers.Input(shape=(NUM_FEATURES,), dtype=tf.float32, name="numerical_features")

    bert_output = bert_model([input_ids, attention_mask]).last_hidden_state
    cls_token = bert_output[:, 0, :]

    x = layers.Concatenate()([cls_token, numerical_features])
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(128, activation="relu", kernel_initializer=initializers.HeNormal())(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dense(64, activation="relu", kernel_initializer=initializers.HeNormal())(x)
    x = layers.LayerNormalization()(x)
    x = layers.Dropout(0.3)(x)
    output = layers.Dense(1)(x)

    model = tf.keras.Model(inputs=[input_ids, attention_mask, numerical_features], outputs=output)

    optimizer = optimizers.AdamW(learning_rate=0.001, weight_decay=1e-6)
    model.compile(optimizer=optimizer, loss="mse")

    # Callbacks
    lr_scheduler = callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=5)
    early_stopping = callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    checkpoint = callbacks.ModelCheckpoint('best_model.h5', monitor='val_loss', save_best_only=True)


    model_info = {
        "TensorFlow version": tf.__version__,
        "Is GPU available": tf.test.is_gpu_available(),
        "Number of Layers": len(model.layers),
        "Layers": [layer.__class__.__name__ for layer in model.layers],
        "Optimizer": model.optimizer.__class__.__name__,
        "Loss Function": model.loss if hasattr(model, 'loss') else 'Not Specified',
    }

    return model, model_info, [lr_scheduler, early_stopping, checkpoint]

